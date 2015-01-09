import mcerp
import scipy.stats
import caravan.settings.globals as glb

class loss:
    _type_int = type(0)
    _type_float = type(5.0)
    _fatalities_labels = (1, 10, 100, 1000, 10000, 100000)
     
    '''
    Class keeping loss estimation methods
    '''
    #TODO: include economic loss function
    def __init__(self, session_id, scenario_id, target_id, geocell_id, bldg_dist, bt_prop, target_prop, bt_dmg):
        self.__bldg_dist = bldg_dist
        self.__bt_prop = bt_prop
        self.__target_prop = target_prop
        self.__bt_dmg = bt_dmg
        self.__scenario_id = scenario_id
        self.__target_id = target_id
        self.__geocell_id = geocell_id
        self.__session_id = session_id
        
    def calculate(self,nighttime=True):
        '''
        Calculate economic, physical (collapses & dg's), social losses
        '''
        self.__nighttime = nighttime
        physical= self.__physical() #FIXME: should be commented OUT AS FOR THE MOMENT IS NOT USED?
        economic = self.__economic()
        social = self.__social(self.__nighttime)
        
        #write to database 
        #self.__write2db()
        
        return [physical,social]

    def __physical(self):
        '''
        Method to calculate physical losses (DGs for location):
        Multiplies bt_dmg distributions with the bt_shares and sums them up to create a single damage pdf for the location
        '''
        loc_dmg = 0
        for row in self.__bldg_dist:
            # share*dmg_pdf(bt)
            loc_dmg += self.__bt_dmg[row[1]]*row[2]
        return loc_dmg

    def __economic(self):
        '''
        Method to calculate economic loss in terms of monetary loss
        '''
        pass


    def __social(self,nighttime):
        '''
        Method to calculate social losses in terms of fatalities
        according to Coburn and Spence 2002
        '''
        # determine if nighttime or not
        if nighttime:
            self.__coeff = 0.5
        else:
            self.__coeff = 0.3

        #1) nr_bdgs (for location): target.bdg_dens*target.geocell_area
        #sometimes we have same lower and higher, therefore use the scalar
        distribution_density = self.__target_prop[0][1][0] if self.__target_prop[0][1][0] == self.__target_prop[0][1][1] else\
                                mcerp.Uniform(self.__target_prop[0][1][0],self.__target_prop[0][1][1])
        
        self.__nr_bdgs = distribution_density * self.__target_prop[0][3]
        
        #self.__nr_bdgs = self.__target_prop[0][1][0] * self.__target_prop[0][3]
        #2) bt_nr (for location): nr_bdgs * bt_share(=building_distributions.freq_dirichlet)
        self.__bt_nr = [(self.__bldg_dist[i][1], self.__nr_bdgs*self.__bldg_dist[i][2]) for i in range(len(self.__bldg_dist))]
        #3) create occpupancy distribution for each bt:
        # assumptions: normally distributed,mean=(occ_max-occ_min/2),std=1/10*range, normal distribution truncated at range bounds of bt_occ[min_occ,max_occ]: bt_occ_min=occ_low*bt_nr; bt_occ_max=occ_high*bt_nr
        self.__bt_occ={}
        
       
        
        for i in range(len(self.__bt_nr)):
            bt_id = self.__bt_nr[i][0]
            for j in range(len(self.__bt_prop)):
                bt_id2 = self.__bt_prop[j][0]
                if bt_id==bt_id2:
                    #bt_nr = self.__bt_nr[i][1]
                    #occ_min = self.__bt_prop[j][2]
                    #occ_max = self.__bt_prop[j][3]
                    occupancy_storey_low = self.__bt_prop[j][2]
                    occupancy_storey_high = self.__bt_prop[j][3]
                    
#                    occupancy_storey = occupancy_storey_low if occupancy_storey_low >= occupancy_storey_high else \
                    occupancy_storey =                    mcerp.Uniform(occupancy_storey_low, occupancy_storey_high)
                    
#                    lower = occupancy_storey_low * self.__bt_nr[i][1]
#                    upper = occupancy_storey_high * self.__bt_nr[i][1]
                    
                    self.__bt_occ[bt_id] = occupancy_storey * self.__bt_nr[i][1]
                    
#                    mu = (upper-lower)/2
#                    sigma = mu/10
#                    a,b = (lower-mu)/sigma,(upper-mu)/sigma
#                    self.__bt_occ[bt_id]=mcerp.uv(scipy.stats.truncnorm(a,b,loc=mu,scale=sigma))
                    
                    #plotting
                    #plotting.plot_pdf(self.__bt_occ[bt_id],'Occupancy',fname='occ_location_bt'+str(bt_id))
        
        #print(str(self.__bt_nr)+" "+str(self.__bt_occ))
         
        #4) calculate fatality distribution for each bt and sum them up:
        self.__fat = 0
        for row in self.__bt_nr:
            bt_id = row[0]
            # coeff*p(dg3.5<dg<dg4.5)*bt_occ + coeff*p(dg>4.5)*bt_occ
            #cdf values:
            p45 = self.__bt_dmg[bt_id] < 4.5
            p35 = self.__bt_dmg[bt_id] < 3.5
            p4 = p45 - p35
            p5 = 1 - p45
            #fatality distribution
            
            self.__fat += self.__coeff*(0.25*p4*self.__bt_occ[bt_id] + p5*self.__bt_occ[bt_id])
        
        return self.__fat

    def write2db(self, db_conn, percentiles): #,scenario_id,target,social):
    #def __write2db(self,scenario_id,target,economic,physical,social):
        '''
        Writes the resulting losses to the risk schema
        Must be called AFTER calculate()
        '''

        fat_labels = self._fatalities_labels
        dist = self.__fat
        fatalities_prob_dist =[v for v in glb.discretepdf(dist, fat_labels)]
        
        exc ='INSERT INTO risk.social_conseq (session_id, scenario_id, geocell_id, target_id, fatalities_prob_dist) VALUES (%s, %s, %s, %s, %s)'
        values = (self.__session_id, self.__scenario_id, self.__geocell_id, self.__target_id, fatalities_prob_dist)
        db_conn.execute(exc, values)

        
#        fatalities_prob_dist = [0] * len(fat_labels)
#        fatalities_percentiles = None
#        isdist =  isinstance(dist, mcerp.UncertainFunction)
#        
#        if not isdist or len(dist._mcpts)==1:
#            #values are stored as numpy items, we want native python items.
#            #from http://stackoverflow.com/questions/9452775/converting-numpy-dtypes-to-native-python-types
#            #we do:
#            val = dist if not isdist else dist._mcpts[0].item()
#            t = type(dist)
#            if not t==self._type_int and not t==self._type_float:
#                raise Exception("fatalities distribution neither float, nor mcerp distribution")
#            
#            fatalities_percentiles = [val]*len(percentiles)
#            
#            for i in range(len(fat_labels)): 
#                if val < fat_labels[i]:
#                    fatalities_prob_dist[i] = 1
#                    break
#            #print("SCALAR: {}".format(str(fatalities_prob_dist)))
#        else:
#            fatalities_percentiles = self.__fat.percentile(percentiles)
#            prev = dist < 0;
#            last = len(fat_labels)-1
#            for i in range(len(fat_labels)):
#                if i == last: 
#                    fatalities_prob_dist[i] = dist >= fat_labels[i-1]
#                    continue
#                tmp = dist < fat_labels[i]
#                fatalities_prob_dist[i] = tmp-prev
#                prev=tmp
            
            
        
#        exc ='INSERT INTO risk.social_conseq (session_id, scenario_id, geocell_id, target_id, est_fatalities, fatalities_prob_dist) VALUES (%s, %s, %s, %s, %s, %s)'
#        values = (self.__session_id, self.__scenario_id, self.__geocell_id, self.__target_id, fatalities_percentiles, fatalities_prob_dist)
        
            
#        #WARNING: mcerp UncertainFunction MIGHT NOW BE COMPOSED OF JUST ONE POINT (bug?)
#        #IN THIS CASE, PERCENTILES FAIL (ALTHOUGH OTHER METHODS WORK).
#        #
#        #THEREFORE WE NEED TO CATCH THE CASE HERE BEFORE ATTEMPTING TO RUN PERCENTILES
#        
#        fatalities_prob_dist = self.tobinsprob(dist) #returns None if pmin (0.05) == pmax (0.95)
#        
#        
#        
#        if fatalities_prob_dist is None:
#            #values are stored as numpy items, we want native python items.
#            #from http://stackoverflow.com/questions/9452775/converting-numpy-dtypes-to-native-python-types
#            #we do:
#            val = dist._mcpts[0].item()
#            #then write to the database a "constant" array of percentiles. FIXME: write also fatalities? (for the moment no)
#            exc ='INSERT INTO risk.social_conseq (session_id, scenario_id, geocell_id, target_id, est_fatalities) VALUES (%s, %s, %s, %s, %s)'
#            values = (self.__session_id, self.__scenario_id, self.__geocell_id, self.__target_id, [val]*len(percentiles),)
#        else:
#            exc ='INSERT INTO risk.social_conseq (session_id, scenario_id, geocell_id, target_id, est_fatalities, fatalities_prob_dist) VALUES (%s, %s, %s, %s, %s, %s)'
#            values = (self.__session_id, self.__scenario_id, self.__geocell_id, self.__target_id, self.__fat.percentile(percentiles), fatalities_prob_dist)
#        
##        try:
##            fatalities_prob_dist = self.tobinsprob(self.__fat)
##            exc ='INSERT INTO risk.social_conseq (session_id, scenario_id, geocell_id, target_id, est_fatalities, fatalities_prob_dist) VALUES (%s, %s, %s, %s, %s, %s)'
##            values = (self.__session_id, self.__scenario_id, self.__geocell_id, self.__target_id, self.__fat.percentile(percentiles), fatalities_prob_dist)
##        except Exception as e:
#            
##            exc ='INSERT INTO risk.social_conseq (session_id, scenario_id, geocell_id, target_id, est_fatalities) VALUES (%s, %s, %s, %s, %s)'
##            values = (self.__session_id, self.__scenario_id, self.__geocell_id, self.__target_id, self.__fat.percentile(percentiles),)
#        
##        exc ='INSERT INTO risk.social_conseq (session_id, scenario_id, geocell_id, target_id, est_fatalities, fatalities_prob_dist) VALUES (%s, %s, %s, %s, %s, %s)'
##        values = (self.__session_id, self.__scenario_id, self.__geocell_id, self.__target_id, self.__fat.percentile(percentiles), self.tobinsprob(self.__fat))

#        db_conn.execute(exc, values)

   
#     @staticmethod
#     def tobinsprob(dist):
#         pmin, pmax = dist.percentile((0.05, 0.95))
#         if pmin == pmax: return None
#         start, distance = getbins(pmin,pmax)
# #        print("pmin,pmax: "+str((pmin,pmax))+ " bins(pmin,pmax): "+str(getbins(pmin,pmax)))
#         probs = [start, distance]
#         prevprob = dist < start-0.5
#         while start < pmax:
#             actualprob = dist < start+0.5
#             probs.append(actualprob - prevprob) 
#             prevprob = actualprob
#             start+=distance
#         
#         #append also last:
#         actualprob = dist < start+0.5
#         probs.append(actualprob - prevprob) 
#             
#         return probs
#     
#     @staticmethod
#     def tobins_old(dist):
#         #deprecated, see tobins
#         
#         x0,x1 = dist.percentile((0.05, 0.95))
#         start = int(x0+0.5)-0.5
#         probs = []
# 
#         while start < x1:
#             prob = (dist < (start+1)) - (dist < start)
#             fatalities = int(start+0.5)
#             probs.append(fatalities)
#             probs.append(prob)
#             start += 1
#             
#         return probs
#     
# def getbins(pmin, pmax):
#     import math
#     
#     prange = pmax-pmin
#     decimaldigits = int(math.floor(math.log10(prange)))
# 
#     maxbins = 10
#     divisor=2
#     min_bins_distance = 1
#     bins_distance = float(10 ** decimaldigits) #NOTE 10 ** 0 =1 INT! this has problems cause we might get division by zero in the loop below
# 
#     last_bins_distance = bins_distance
# 
#     while prange/bins_distance < maxbins:
#         last_bins_distance = bins_distance
#         bins_distance/=divisor 
#         divisor = 5 if divisor== 2 else 2
#         if divisor == 2: #meaning it was 5, so we dropped one decimal pos down
#             decimaldigits-=1 #ACTUALLY NOT USEED, HOWEVER WE KEEP IT HERE
#     
#     pmin1 = bins_distance*int(pmin/bins_distance)
#     tmp, tmp2 = pmax/bins_distance, int(pmax/bins_distance)
#     pmax1 = (bins_distance*tmp2) + (1 if tmp!=tmp2 else 0)
#     
#     pmin2 = last_bins_distance*int(pmin/last_bins_distance)
#     tmp, tmp2 = pmax/last_bins_distance, int(pmax/last_bins_distance)
#     pmax2 = (last_bins_distance*tmp2) + (1 if tmp!=tmp2 else 0)
#     
#     if abs((pmax2-pmin2)/last_bins_distance - maxbins) < abs((pmax1-pmin1)/bins_distance - maxbins):
#         bins_distance = last_bins_distance
#         
# #    if abs(prange/last_bins_distance - maxbins) < abs(prange/bins_distance - maxbins):
# #    bins_distance = last_bins_distance
# 
#     if bins_distance < min_bins_distance:
#         bins_distance = min_bins_distance
# 
#     firstelm = bins_distance*int(pmin/bins_distance)
# 
# #    while firstelm < pmin: #for safety (round errors made firstelem lower than pmin)
# #        firstelm = bins_distance*math.ceil(0.5+pmin/bins_distance)    
# 
#     #round to int if it is the case to avoid rounding errors
#     int_bins_distance = int(bins_distance)
#     if bins_distance == int_bins_distance:
#         bins_distance = int_bins_distance
#         k = int(firstelm)
#     else:
#         k=firstelm
#     
#     return k, bins_distance
# #    while k < pmax:
# #        val = k
# #        yield val
# #        k+=bins_distance
# #    yield k #append last
    
    
if __name__ == "__main__":
    import sys
    print(str(loss.tobinsprob(mcerp.Normal(float(sys.argv[1]),float(sys.argv[2])))))