
class exposure:
    '''
    Class keeping methods to get exposure information for locations from the database
    '''
    def __init__(self, db_conn, geocell_id):
        self.__db_conn = db_conn
        self.__geocell_id = geocell_id
        #self.__pgsql = postgresql_module.postgresql(self.__db_conn)
    
        #TODO: building_tpes (value+occupancy)
        #TODO: geocells (get geometry)
        #TODO: targets (area + pop-dens + bdg-dens) : implement coorect database structure

        ## get building and population density and area of the reference geocell
        #self.__query = 'SELECT geocell_id,bdg_density,pop_density,geocell_area FROM exposure.targets WHERE geocell_id={}'.format(self.__geocell_id)
        #self.__target_prop = self.__pgsql.execute(self.__query)

        ## get building distribution for the location
        #self.__query = 'SELECT geocell_id,building_type,freq_dirichlet FROM exposure.building_distributions WHERE geocell_id={}'.format(self.__geocell_id)
        #self.__bldg_dist =self.__pgsql.execute(self.__query)

        ## get according building_type vulnerability-distribution, occupancy (low + high) and construction cost
        #self.__query = 'SELECT gid,vuln_ems98,occupancy_storey_low,occupancy_storey_high,construction_cost FROM exposure.building_types WHERE gid IN (SELECT building_type FROM exposure.building_distributions WHERE geocell_id={})'.format(self.__geocell_id)
        #self.__bt_prop = self.__pgsql.execute(self.__query)

        ## get coordinates of location
        #self.__query = 'SELECT ST_X(the_geom),ST_Y(the_geom) FROM exposure.targets WHERE geocell_id={}'.format(self.__geocell_id)
        #self.__target_loc = self.__pgsql.execute(self.__query)

        #del self.__pgsql
        
        #ADDED BY ME:
        
        #I don't format strings but follow psycopg2 doc, passing two args and using "%s" in the first one
        #In any case, use format instead of % cause the latter is not (yet) deprecated but the former it's more PY3 compliant
        #Form reference, see https://docs.python.org/2/library/string.html#formatstrings
        query = 'SELECT geocell_id,bdg_density,pop_density,geocell_area FROM exposure.targets WHERE geocell_id=%s' #.format(geocell_id)
        self.__target_prop = db_conn.fetchall(query, (geocell_id,) )

        # get building distribution for the location
        query = 'SELECT geocell_id, building_type, freq_dirichlet FROM exposure.building_distributions WHERE geocell_id=%s' #.format(geocell_id)
        self.__bldg_dist = db_conn.fetchall(query,(geocell_id,))
        
        # get according building_type vulnerability-distribution, occupancy (low + high) and construction cost
        query = 'SELECT gid, vuln_ems98, occupancy_storey_low, occupancy_storey_high, construction_cost FROM exposure.building_types WHERE gid IN (SELECT building_type FROM exposure.building_distributions WHERE geocell_id=%s)' #.format(geocell_id)
        self.__bt_prop = db_conn.fetchall(query, (geocell_id,))

        # get coordinates of location
        query = 'SELECT ST_X(the_geom),ST_Y(the_geom) FROM exposure.targets WHERE geocell_id=%s' #.format(geocell_id)
        self.__target_loc = db_conn.fetchall(query, (geocell_id,))

    @property
    def bldg_dist(self):
        '''
        Get building type distribution of the locations the class was instanced with
        '''
        #change from list of tuples to list of lists
        self.__return=[]
        for elem in self.__bldg_dist:
            self.__return.append(list(elem))
        return self.__return

    @property
    def bt_prop(self):
        '''
        Get building type vulnerability relations of the locations the class was instanced with
        '''
        #change from list of tuples to list of lists
        self.__return=[]
        for elem in self.__bt_prop:
            self.__return.append(list(elem))
        return self.__return

    @property
    def target_prop(self):
        '''
        Get properties of targets [(gid,[blg_dens],[pop_dens],geocell area)]
        '''
        return self.__target_prop

    @property
    def target_loc(self):
        '''
        Get longitude and latitude of target
        '''
        return self.__target_loc
