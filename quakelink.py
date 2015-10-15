import sys, json,time, mcerp

from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, Request, build_opener
from urllib import urlencode


def quakelink(url, params=None, req_type="GET", data=None, headers=None):
	post_req = ["POST", "PUT"]
	get_req = ["GET", "DELETE"]

	if headers is None:
		headers = {}

	if params is not None:
		url += "?" + urlencode(params)

	if req_type not in post_req + get_req:
		raise IOError("Wrong request type \"%s\" passed" % req_type)
	if req_type in post_req and data is not None:
		headers["Content-Length"] = len(data)

	director = build_opener(*[])

	if req_type in post_req:
		data = bytes(data)
		req = Request(url, headers=headers, data=data)
	else:
		req = Request(url, headers=headers)

	req.get_method = lambda: req_type
	result = director.open(req)

	return {
		"httpcode": result.code,
		"headers": result.info(),
		"content": result.read()
	}


def subquery(condition, min, max):
	subquery = []
	if min:
		subquery.append("%s >= %s" % (condition, str(min)))

	if max:
		subquery.append("%s < %s" % (condition, str(max)))

	return subquery

if __name__ == "__main__":
	import caravan.settings.globalkeys as gk
	import caravan.settings.globals as glb

	from caravan.core.core import caravan_run as run
	from caravan.core.runutils import RunInfo

	RUNS ={}

	updated=glb.quakelink_conf['updated']


	while True:
		data = []
		data += subquery("mag", glb.quakelink_conf['min_mag'], glb.quakelink_conf['max_mag'])
		data += subquery("lat", glb.quakelink_conf['min_lat'], glb.quakelink_conf['max_lat'])
		data += subquery("lon", glb.quakelink_conf['min_lon'], glb.quakelink_conf['max_lon'])

		if updated:
			data.append('updated>%s' % updated)

		cont = quakelink(glb.quakelink_conf['url'], data=" and ".join(data), req_type='POST')
		data = json.loads(cont["content"])
		updated = data["seiscomp"]["lastUpdate"]

		for jsonData in data["seiscomp"]["events"]:
			jsonData.update({u'tess_ids': [1, 2, 3, 4, 5, 6, 7], u'eid': '%s' % jsonData["eventID"],u'ipe': 3, u'dep': jsonData["depth"], u'gm_only': False, u'str': u'90', u'mcerp_npts': 40})
			key_mcerpt_npts = gk.DNP
			mcerp.npts = glb.mcerp_npts if not key_mcerpt_npts in jsonData else glb.cast(key_mcerpt_npts, jsonData[key_mcerpt_npts])

			runinfo = RunInfo(jsonData)

			ret= {}
			if runinfo.status()==1: #running, ok
				runinfo.msg("Process starting at {0} (server time)".format(time.strftime("%c")))

				try:
					run(runinfo)
				except Exception, e:
					print "Run-Error for event %s: %s" % (jsonData["eventID"],str(e))

				RUNS[runinfo.session_id()] = runinfo 
				ret = {'session_id':runinfo.session_id(), 'scenario_id':0}
			else:
				ret = {'error': runinfo.errormsg or "Unknown error (please contact the administrator)"}

			print RUNS
