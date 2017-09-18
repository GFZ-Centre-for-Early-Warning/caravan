# -* coding: utf-8 -*-
import caravan.settings.globals as glb
import os
import codecs
import numpy as np
import pylatex
import scipy
import shapely.wkt

import jinja2
from jinja2 import Template

#TODO: use different directory
#TODO: check if report exists for session id
#TODO: add probability of collapse for most vulnerable buildings

def bufferp(polygon,size):
    '''
    Generates size% buffer around rectangle (extent)
    '''
    #round to 2 digits
    polygon = [round(p,2) for p in polygon]
    #size% increase
    inc1 = abs(polygon[0]-polygon[2])*size/100.
    inc2 = abs(polygon[1]-polygon[3])*size/100.
    inc = [-inc1,-inc2,inc1,inc2]
    return tuple([round(p+i,2) for i,p in zip(inc,polygon)])

def hex2rgb(hexval):
    '''
    Converts hexadecimal code to rgb
    '''
    hexmap={'0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'A':10,'B':11,'C':12,'D':13,'E':14,'F':15}
    #omit leading<#>
    red   = 16*hexmap[hexval[1]]+hexmap[hexval[2]]
    green = 16*hexmap[hexval[3]]+hexmap[hexval[4]]
    blue  = 16*hexmap[hexval[5]]+hexmap[hexval[6]]
    return ' '.join([str(red),str(green),str(blue)])

##create plots from data
def generate_plot(impact_data,extent,epicentre,measure,fname,ptype='median'):
    '''
    Generates plot
    '''
    #settings
    #subprocess.check_output(['gmtset','FONT_ANNOT_PRIMARY=12p'])
    os.system('gmtset FONT_ANNOT_PRIMARY=12p')
    #subprocess.check_output(['gmtset','FONT_ANNOT_SECONDARY=12p'])
    os.system('gmtset FONT_ANNOT_SECONDARY=12p')
    #subprocess.check_output(['gmtset','FONT_LABEL=12p'])
    os.system('gmtset FONT_LABEL=12p')
    #generate basemap
    extent = shapely.wkt.loads(extent[0][0]).bounds
    extent = bufferp(extent,10)
    #tick = max([round(round(abs(extent[0]-extent[2])/4,1)*2)/2,round(round(abs(extent[1]-extent[3])/4,1)*2)/2])
    tick = min([round(abs(extent[0]-extent[2])/4,1),round(abs(extent[1]-extent[3])/4,1)])

    #srtm background
    #cmd='grdcut -R{}/{}/{}/{} etopo1_bedrock.nc -Getopo1.grd'.format(extent[0],extent[2],extent[1],extent[3])
    cmd='grdcut -R{}/{}/{}/{} kyz.grd -Gkyz_cut.grd'.format(extent[0],extent[2],extent[1],extent[3])
    os.system(cmd)
    #cmd='grdgradient etopo1.grd -A45 -Ne0.5 -Getopo1_shadow.grd'
    cmd='grdgradient kyz_cut.grd -A45 -Ne0.5 -Gkyz_shadow.grd'
    os.system(cmd)
    #cmd='grdimage etopo1.grd -Ctopo_water.cpt -R -JM5i -Y2i -B{}WSne -K > {}'.format(tick,fname)
    cmd='grdimage kyz_cut.grd -Ctopo_water.cpt -R -JM5i -Y2i -B{}WSne -K > {}'.format(tick,fname)
    os.system(cmd)

    #coastlines to mark continent
    cmd='pscoast -R -J -Gc -K -O >> {}'.format(fname)
    os.system(cmd)

    #etopo background
    cmd='grdimage kyz_cut.grd -Ctopo.cpt -J -R -O -K >> {}'.format(fname)
    os.system(cmd)
    cmd='grdimage kyz_cut.grd -Ikyz_shadow.grd -Ctopo.cpt -J -R -K -O >> {}'.format(fname)
    os.system(cmd)

    #coastlines
    cmd='pscoast -R -J -Q -K -O >> {}'.format(fname)
    os.system(cmd)
    cmd='pscoast -R -J -Df -Na -W0.5,#808080 -K -O >> {}'.format(fname)
    os.system(cmd)

    # Determine colors for data
    # Where color is determined based on values of the measure
    #create cmap and colors (depending on plot type)
    if (measure == 'gm'):
        #4,5,6,7,8,9,10,11
        cmap = {'4':'#FFFF11','5':'#FFD700','6':'#FFAA00','7':'#FF5500','8':'#FF0000','9':'#D00000','10':'#A00000','11':'#900000'}
        idx = 2
        #bins are halfopen!! 4 -> [3.5,4.5) except last [10.5,12]
        bins = [3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,12]
        label = 'Macroseismic Intensity'
        annotations = ['IV','V','VI','VII','VIII','IX','X','XI']
        delta=0
    elif (measure == 'social'):
        #0,1,10,20,50,100,200,500,1000
        cmap = {'0':'#008000','1':'#FFD700','10':'#FF4500','20':'#FF0000','50':'#E00000','100':'#CC0000','200':'#CC0000','500':'#CC0000','1000':'#CC0000'}
        idx = 3
        bins = [0,1,10,20,50,100,200,500,1000,1e6]
        label = 'Casualties'
        annotations=['0','1','10','20','50','100','200','500','1000']
        delta=0.1
    elif (measure == 'economic'):
        #idx = 4
        pass
    else:
        pass

    if (ptype=='median'):
        idx_type=-1
    else:
        pass

    #create a gmt polygon file like
    #> -Gfcolor@50
    #x1 y1
    #x2 y2
    #x3 y3
    #...
    init=1
    datafname=fname[:-3]+'.gmt'
#######
    #used for debugging geometry if (some were invalid)
######
    #count=1
    #j = 0
    #datafname=fname[:-3]+'1.gmt'
    #while j < len(impact_data):
    #    #split files in smaller junks
    #    if (j <= 1000*count):
    #        #determine colorvalue from cmap
    #        h1 = scipy.histogram([float(impact_data[j][idx][idx_type])],bins)
    #        i = [i for i,h in enumerate(h1[0]) if h==1][0]
    #        color = cmap[str(int(round(bins[i])))]
    #        #write to file
    #        if init:
    #            filehandle = open(datafname,'w')
    #            filehandle.write('> -G{}@50\n'.format(color))
    #            init=0
    #        else:
    #            filehandle.close()
    #            filehandle = open(datafname,'a')
    #            filehandle.write('\n> -G{}@50\n'.format(color))
    #        #get wkt string of polygons only coordinates 'x1 y1,x2 y2,...,xn yn'
    #        coords = impact_data[j][0][9:-2]
    #        #rewrite to file in gmt style
    #        filehandle.write(coords.replace(',','\n'))
    #        j=j+1
    #    else:
    #        filehandle.close()
    #        init=1
    #        #dont skip a geocell --> don't increase j here just increase count
    #        count = count + 1
    #        datafname=fname[:-3]+str(count)+'.gmt'
    #    #close file
    #    filehandle.close()
    #plot cells using psxy
    #for i in range(count):
    #    print(i)
    #    cmd='psxy -R -J -B -L {} -O -K >> {}'.format(fname[:-3]+str(i+1)+'.gmt',fname)
    #    os.system(cmd)
#######
    with codecs.open(datafname,'w','utf-8') as filehandle:
        for row in impact_data:
            #determine colorvalue from cmap
            h1 = scipy.histogram([float(row[idx][idx_type])],bins)
            i = [i for i,h in enumerate(h1[0]) if h==1][0]
            color = cmap[str(int(round(bins[i])))]
            #write to file
            if init:
                filehandle.write('> -G{}@50\n'.format(color))
                init=0
            else:
                filehandle.write('\n> -G{}@50\n'.format(color))
            #get wkt string of polygons only coordinates 'x1 y1,x2 y2,...,xn yn'
            coords = row[0][9:-2]
            #rewrite to file in gmt style
            coords = coords.replace(',','\n')
            filehandle.write(coords.encode('UTF-8'))

    #plot cells using psxy
    cmd='psxy -R -J -L {} -O -K >> {}'.format(datafname,fname)
    os.system(cmd)

    #plot epicentre (if gm)
    if measure == 'gm':
        cmd='psxy -R -J -Sa0.2i -Gblack -O -K << EOF >> {} \n{} {}\nEOF'.format(fname,epicentre[0],epicentre[1])
        os.system(cmd)

    #towns
    cmd='psxy -R -J -St0.1i -Gblack {} -O -K >> {}'.format('towns.gmt',fname)
    os.system(cmd)
    cmd='pstext -R -J {} -F+jBL -O -K >> {}'.format('towns.gmt',fname)
    os.system(cmd)

    #create cpt
    f=codecs.open(measure+'_colors.cpt','w','utf-8')
    init=1
    for i in range(len(bins)-1):
        val = int(round(bins[i]))
        col = hex2rgb(cmap[str(val)])
        val2 = int(round(bins[i+1]))
        if init:
            line = str(val+delta)+' '+col+' ' + str(val2)+' '+col+' ;'+annotations[i]
            init=0
        else:
            line = '\n'+ str(val)+' '+col+' ' + str(val2)+' '+col+' ;'+annotations[i]
        f.write(line)
    f.close

    #plot scale
    logarithmic=' '
    #if measure=='social':
    #    logarithmic=' -Q '
    cmd='psscale -D2.5i/-0.4i/4i/.3ih -Ba1:"{}":{}-C{}_colors.cpt -O >> {}'.format(label,logarithmic,measure,fname)
    print cmd
    os.system(cmd)

    #create pdf
    cmd="psconvert -A -P -Tf {}".format(fname)
    os.system(cmd)

def generate_barplot(impact_data,locations_data,measure,fname):
    '''
    Function to generate barplot
    '''
    roman_numerals = ['IV','V','VI','VII','VIII','IX','X','XI']
    #settings
    #subprocess.check_output(['gmtset','FONT_ANNOT_PRIMARY=12p'])
    os.system('gmtset FONT_ANNOT_PRIMARY=12p')
    #subprocess.check_output(['gmtset','FONT_ANNOT_SECONDARY=12p'])
    os.system('gmtset FONT_ANNOT_SECONDARY=12p')
    #subprocess.check_output(['gmtset','FONT_LABEL=12p'])
    os.system('gmtset FONT_LABEL=12p')

    if (measure == 'gm'):
        bins=[4,5,6,7,8,9,10,11]
        idx = 2
        label = 'Intensity'
        cmap = ['#FFFF11','#FFD700','#FFAA00','#FF5500','#FF0000','#D00000','#A00000','#900000']
        closeit = ' -K'
    elif (measure == 'social'):
        bins=[0,1,10,20,50,100,200,500,1000]
        idx = 3
        label = 'Fatalities'
        cmap = ['#008000','#FFD700','#FF4500','#FF0000','#E00000','#CC0000','#CC0000','#CC0000','#CC0000']
        closeit = ''
    elif (measure == 'economic'):
        #idx = 4
        pass
    else:
        pass

    #gather data
    #largest population cell id
    geocell_id=locations_data[0][0]
    j = [i for i,row in enumerate(impact_data) if row[1]==geocell_id][0]
    distribution = impact_data[j][idx]

    #write gmt file
    #datafname = fname[:-3]+'.gmt'
    #f=codecs.open(datafname,'w','utf-8')
    #init=1
    #for i in range(len(bins)):
    #if init:
    #        #f.write(str(bins[i])+' '+str(distribution[i])+' -G'+cmap[i])
    #        f.write(str(bins[i])+' '+str(distribution[i]))
    #        init=0
    #    else:
    #        #f.write('\n'+str(bins[i])+' '+str(distribution[i])+' -G'+cmap[i])
    #        f.write('\n'+str(bins[i])+' '+str(distribution[i]))
    #f.close

    #generate plot
    #create cpt
    f=codecs.open('barplot.cpt','w','utf-8')
    for i in range(len(bins)-1):
        line=str(bins[i])+' '+cmap[i]+' '+str(bins[i+1])+' '+cmap[i]+'\n'
        f.write(line)
    f.close()

    cmd='psxy -Jx1/4 -R{}/{}/0/1 -W0.5p -Sb0.2i -Cbarplot.cpt -B1/.2:"Probability":/:"{}":WSne:."Geocell id {}":{} << EOF > {}'.format(bins[0],bins[-1],label,geocell_id,closeit,fname)
    #file did not work!??!? with psxy on server (on local gmt same version it did)??!! --> quick and dirty solution
    for i in range(len(bins)):
        cmd=cmd+'\n'+str(bins[i])+' '+str(distribution[i])+' '+str(bins[i])
    os.system(cmd)

    #add roman numerals
    if measure=='gm':
        cmd='pstext -R -J -O -Gwhite -C20% -N << EOF >> {}'.format(fname)
        for i in range(len(bins)):
            cmd=cmd+'\n'+str(bins[i])+' '+'-0.12'+' '+roman_numerals[i]
        os.system(cmd)

    #create pdf
    cmd="psconvert -A -P -Tf {}".format(fname)
    os.system(cmd)

def report(session_id):
    '''
    Function that generates a report for the event
    '''
    ###########
    #working directory
    ###########
    old_cwd = os.getcwd() #for changing back at the end
    new_cwd = os.path.dirname(os.path.realpath(__file__))+'/static/report/'
    os.chdir(new_cwd)
    print os.getcwd()
    ###########
    #gather data
    ###########
    conn = glb.connection(async=True)
    #--event
    event = conn.fetchall("""SELECT
        se.gid,
        sc.mag,
        sc.epi_lat,
        sc.epi_lon,
        sc.ipo_depth,
        sc.fault_strike,
        sc.fault_dip,
        sc.fault_style,
        sc.gmpe_id
        FROM
        processing.sessions AS se
        LEFT JOIN
        processing.scenarios AS sc ON (sc.gid=se.scenario_id)
        WHERE
        se.gid=%s;""",(session_id,))

    #store info for event remove {} of arrays and store (val1,val2) where val1 and val2 determines the bounds of a uniform distribution
    event_mag = event[0][1]
    event_lat = event[0][2]
    event_lon = event[0][3]
    event_z   = event[0][4]
    event_strike = event[0][5]
    event_dip = event[0][6]

    faulting= conn.fetchall("""SELECT gid,name FROM hazard.faulting_styles""")
    event_fault = [row[0] for row in faulting if row[0]==event[0][7]]
    #generate faulting line for report
    if len(event_fault)==0:
        sof=''
    else:
        sof='Assumed style of faulting is {} with dip {:3.2f}+/-{:3.2f} and strike {:3.2f}+/-{:3.2f}. '.format(event_fault[0],(event_dip[0]+event_dip[1])/2.,abs(event_dip[0]-event_dip[1])/2.,(event_strike[0]+event_strike[1])/2.,abs(event_strike[0]-event_strike[1])/2.)

    gmpes= conn.fetchall("""SELECT gid,name FROM hazard.gmpes""")
    event_gmpe = [row[1] for row in gmpes if row[0]==event[0][8]][0]

    #--largest agglomerations (geocells --> associate name later on)
    locations = conn.fetchall("""SELECT
        t.geocell_id,
        ST_AsText(t.the_geom) as geom,
        Round(t.pop_density[array_length(t.pop_density,1)]*t.geocell_area) as pop,
        GM.ground_motion
        FROM
        processing.ground_motion as GM
        LEFT JOIN
        exposure.targets AS t ON (t.geocell_id=GM.geocell_id)
        WHERE
        GM.session_id=%s
        ORDER BY pop DESC;""",(session_id,))

    #round inhabitants
    inhab = locations[0][2]
    #select magnitude order for rounding (one less than value at least 10)
    size=max(10,10**(int(np.log10(inhab))-1))
    diff=abs(size-inhab%size)
    inhab = inhab + (-1*(inhab%size<size/2.)+(1-(inhab%size<size/2.)))*diff

    #--impact
    #-- For  1) gm plot
    #--      2) fat plot
    #--      3) eco plot
    impact = conn.fetchall("""SELECT ST_AsText(ST_Transform(G.the_geom,4326)) AS geometry,
           GM.geocell_id,
           GM.ground_motion,
           risk.social_conseq.fatalities_prob_dist,
           risk.econ_conseq.total_loss
        FROM
            processing.ground_motion as GM
            LEFT JOIN
            risk.social_conseq ON (risk.social_conseq.geocell_id = GM.geocell_id and risk.social_conseq.session_id =  GM.session_id)
            LEFT JOIN
            risk.econ_conseq ON (risk.econ_conseq.geocell_id = GM.geocell_id and risk.econ_conseq.session_id = GM.session_id)
            LEFT JOIN
            exposure.geocells as G ON (G.gid = GM.geocell_id)
            WHERE
            GM.session_id=%s;""",(session_id,))

    #--gm distribution largest agglomeration
    #----> in python from "impact" and "largest agglomerations"
    #see generate_barplot function

    #--area felt
    area = conn.fetchall("""SELECT
        SUM(t.geocell_area)
        FROM
        processing.ground_motion as GM
        LEFT JOIN
        exposure.targets AS t ON (t.geocell_id=GM.geocell_id)
        WHERE
        GM.session_id=%s;""",(session_id,))
    #area = conn.fetchall("""SELECT
    #    SQRT(SUM(t.geocell_area))/3.14159265359
    #    FROM
    #    processing.ground_motion as GM
    #    LEFT JOIN
    #    exposure.targets AS t ON (t.geocell_id=GM.geocell_id)
    #    WHERE
    #    GM.session_id=%s;""",(session_id,))

    #--maximum intensity
    #----> in python from "impact"
    maximum_intensity = [float(row[2][-1]) for row in impact]
    #store geocell id and maximum median intensity as tuple
    roman_numerals = ['0','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
    maximum_intensity = [(impact[i][1],roman_numerals[int(round(x))]) for i,x in enumerate(maximum_intensity) if x==max(maximum_intensity)][0]

    #--Building types
    bt = conn.fetchall("""SELECT GM.geocell_id,
           BD.building_type,
           BD.freq_dirichlet,
           BD.freq_storeys,
           BT.vuln_ems98,
           BT.occupancy_storey_low,
           BT.occupancy_storey_high,
           BT.construction_cost,
           BT.total_value,
           BT.name
        FROM
            processing.ground_motion as GM
            LEFT JOIN
            exposure.building_distributions AS BD ON (BD.geocell_id = GM.geocell_id)
            LEFT JOIN
            exposure.building_types AS BT ON(BT.gid=BD.building_type)
            WHERE
            GM.session_id=%s;""",(session_id,))

    #generate data for exposure table: main 3 building types, approx. share, most likely VC
    bt_freq = {}
    bt_vc = {}
    bt_name = {}
    for row in bt:
        if str(row[1]) not in bt_freq.keys():
            #frequency (single value)
            bt_freq[str(row[1])] = row[2]
            #vulnerability (list)
            bt_vc[str(row[1])] = row[4]
            #only needed once
            bt_name[str(row[1])] = row[-1]
        else:
            #frequency (single value)
            bt_freq[str(row[1])] += row[2]
            #vulnerability (list)
            bt_vc[str(row[1])] = [x+y for x,y in zip(row[4],bt_vc[str(row[1])])]

    #create averages
    for key in bt_freq.keys():
        bt_freq[key]=bt_freq[key]/len(locations)
        bt_vc[key]=[x/len(bt) for x in bt_vc[key]]

    #select m dominant types
    m = 3
    exposure_idx=[]
    #adjust m to maximum possible size if necessary
    if m>len(bt_freq.keys()):m=len(bt_freq.keys())

    while len(exposure_idx)<m:
        max_val=0
        for key in [k for k in bt_freq.keys() if k not in exposure_idx]:
            if bt_freq[key]>max_val:
                max_val = bt_freq[key]
                idx = key
        exposure_idx.append(idx)
        max_val=0

    #create lists for table
    exposure_bt=[bt_name[key] for key in exposure_idx]
    exposure_freq=[bt_freq[key] for key in exposure_idx]
    vc_map = ['A','B','C','D','E','F']
    exposure_vc_tmp=[bt_vc[key] for key in exposure_idx]
    exposure_vc=[]
    for l in exposure_vc_tmp:
        exposure_vc.append(vc_map[[i for i,x in enumerate(l) if x == max(l)][0]])

    #format vc string
    vc_string = set(exposure_vc)
    if len(vc_string) == 1:
        vc_string = ' '+str(vc_string)
    elif len(vc_string) == 2:
        vc_string = 'es '+' and '.join(vc_string)
    else:
        vc_string = ', '.join(exposure_vc[:-1])+' and '+exposure_vc[-1]

    #--pop_density distribution (rural/urban)
    #----> in python from "largest agglomerations"
    population=sum([row[2] for row in locations])
    if population >= 1e6:
        affect_descr = 'an urban region'
    elif population >= 1e5:
        affect_descr = 'a denser populated region'
    else:
        affect_descr = 'a rural region'

    fat_by_loc = conn.fetchall("""SELECT
        t.geocell_id,
        ST_AsText(t.the_geom) as geom,
        Round(t.pop_density[array_length(t.pop_density,1)]*t.geocell_area) as pop,
        GM.ground_motion,
        r.fatalities_prob_dist[array_upper(r.fatalities_prob_dist,1)] AS fat
        FROM
        processing.ground_motion as GM
        LEFT JOIN
        exposure.targets AS t ON (t.geocell_id=GM.geocell_id)
        LEFT JOIN
        risk.social_conseq AS r ON (r.geocell_id = GM.geocell_id and r.session_id = GM.session_id)
        WHERE
        GM.session_id=%s
        ORDER BY fat DESC;""",(session_id,))

    #--most likely range of fatalities by n mostly affected (by median value) agglomerations
    #----> in python from "fat_by_loc"
    #keep data order by size of location(geocell) geocell ids
    n=10
    fat_order = [fat_by_loc[i][0] for i in range(n)]
    rows = [row for row in impact if row[1] in fat_order]
    data_id = [row[1] for row in rows]
    #extract most likely value
    text=['0-1','1-10','10-20','20-50','50-100','100-200','200-500','500-1000']
    data=[]
    for row in rows:
        data.append(text[[i for i,x in enumerate(row[3][:-1]) if x==max(row[3][:-1])][0]])
    #find order for geocell_ids
    sort_order=[]
    for di in data_id:
        sort_order.append([i for i,x in enumerate(fat_order) if x == di][0])
    #fatalities sorted by size of agglomeration
    fat_sorted = [data[i] for i in sort_order]
    fat_pop = [fat_by_loc[i][2] for i in range(n)]
    roman_numerals = ['0','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
    fat_int = [int(round(row[3][-1])) for row in rows]

    #total sum of median fatalities
    fat_tot = sum([float(row[4]) for row in fat_by_loc])
    fat_range = [0,1,10,20,50,100,200,500,1000,1e4,1e5]
    diff = [abs(x-fat_tot) for x in fat_range]
    idx = [i for i,x in enumerate(diff) if x==min(diff)][0]
    fat_tot = str(fat_range[idx])+'-'+str(fat_range[idx+1])


    extent_gm = conn.fetchall("""SELECT ST_AsText(ST_Extent((ST_Transform(G.the_geom,4326)))) as bb
            FROM
            processing.ground_motion as GM
            LEFT JOIN
            exposure.geocells as G ON (G.gid = GM.geocell_id)
            WHERE
            GM.session_id=%s;""",(session_id,))
    
    extent_social = conn.fetchall("""SELECT ST_AsText(ST_Extent((ST_Transform(G.the_geom,4326)))) as bb
            FROM
            risk.social_conseq as S
            LEFT JOIN
            exposure.geocells as G ON (G.gid = S.geocell_id)
            WHERE
            S.session_id=%s AND S.fatalities_prob_dist[10] > 0;""",(session_id,))
           # S.session_id=%s AND \'{1,0,0,0,0,0,0}\' <>S.fatalities_prob_dist;""",(session_id,[1.,0.,0.,0.,0.,0.,0.]))
    
    #set to ground motion extent if no fatalities
    print(extent_social)
    if len(extent_social)==0:
	    extent_social = extent_gm
    
    fat_by_loc = conn.fetchall("""SELECT
        t.geocell_id,
        ST_AsText(t.the_geom) as geom,
        Round(t.pop_density[array_length(t.pop_density,1)]*t.geocell_area) as pop,
        GM.ground_motion,
        r.fatalities_prob_dist[array_upper(r.fatalities_prob_dist,1)] AS fat
        FROM
        processing.ground_motion as GM
        LEFT JOIN
        exposure.targets AS t ON (t.geocell_id=GM.geocell_id)
        LEFT JOIN
        risk.social_conseq AS r ON (r.geocell_id = GM.geocell_id and r.session_id = GM.session_id)
        WHERE
        GM.session_id=%s
        ORDER BY fat DESC;""",(session_id,))

    conn.close()
    #################
    # Create plots
    #################
    generate_plot(impact,extent_gm,[event_lon[0],event_lat[0]],'gm',new_cwd+'/gm.ps','median')
    generate_plot(impact,extent_social,[event_lon[0],event_lat[0]],'social',new_cwd+'/social.ps','median')
    generate_barplot(impact,locations,'gm',new_cwd+'/gm_barplot.ps')

    #################
    # Compose document
    #################
    #use jinja
    latex_jinja_env = jinja2.Environment(
        block_start_string = '\BLOCK{',
        block_end_string = '}',
        variable_start_string = '\VAR{',
        variable_end_string = '}',
        comment_start_string = '\#{',
        comment_end_string = '}',
        line_statement_prefix = '%%',
        line_comment_prefix = '%#',
        trim_blocks = True,
        autoescape = False,
        loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    template = latex_jinja_env.get_template('report-template.tex')
    filehandle=open('./report.tex','w')
    filehandle.write(template.render(lat         = '{:3.2f}'.format(    event_lat[0]                          ),
                                     lat_err     = '{:3.2f}'.format(    event_lat[1]                          ),
                                     lon         = '{:3.2f}'.format(    event_lon[0]                          ),
                                     lon_err     = '{:3.2f}'.format(    event_lon[1]                          ),
                                     z           = '{:3.2f}'.format(   (event_z[0]      + event_z[1])  /2.    ),
                                     z_err       = '{:3.2f}'.format(abs(event_z[0]      - event_z[1])  /2.    ),
                                     mag         = '{:2.1f}'.format(   (event_mag[0]    + event_mag[1])/2.    ),
                                     mag_err     = '{:2.1f}'.format(abs(event_mag[0]    - event_mag[1])/2.    ),
                                     sof         = sof                                                         ,
                                     largest     = '{}'.format(    locations[0][0]                            ),
                                     inhab       = '{:d}'.format(int(inhab)                                   ),
                                     gmpe        = '{}'.format(    event_gmpe                                 ),
                                     max_gm_loc  = '{}'.format(    maximum_intensity[0]                       ),
                                     max_gm      = '{}'.format(    maximum_intensity[1]                       ),
                                     area        = '{}'.format(int(round(area[0][0]/10)*10)                   ),
                                     n           = '{}'.format(    n                                          ),
                                     region      = '{}'.format(    affect_descr                        ),
                                     m           = '{}'.format(    m                                     ),
                                     exposure    = zip(exposure_bt,[round(f,2) for f in exposure_freq],exposure_vc)                  ,
                                     vc_string   = '{}'.format(    vc_string                             ),
                                     fat_tot     = '{}'.format(    fat_tot                               ),
                                     loss        = zip(fat_order,fat_sorted,[int(f) for f in fat_pop],fat_int )
           ))
    filehandle.close()

    #create pdf (run twice to get references right)
    os.system('pdflatex report.tex')
    os.system('pdflatex report.tex')

    #go back to old wd
    os.chdir(old_cwd)

