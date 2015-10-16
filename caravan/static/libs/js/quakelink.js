function quakelink(){
	var last_session = 0;

	$('.quakelink').find('td').each(function(i,elm){
		var $elm = $(elm);
		var k = $elm.data('submit-key');
		var v = $elm.data('submit-value');
		if(k == "session_id" && v > last_session){
			last_session = v;
		}
	});

	console.log("LastSession:" + last_session);

	$.post('query_quakelink_data', JSON.stringify({'session_id': last_session}), function (data, textStatus, jqXHR) {

			if(!data){return;}

			var events = data.new_events;
			if (!events || !events.length) {
				return;
			}

			$('.quakelink tr').last().after(events);

		}, "json").fail(function () {
			//NOTE: we SHOULD NEVER BE here (SEE SERVER SIDE CODE). LEFT HERE FOR SAFETY
		}).always(function () {
			setTimeout(quakelink,5000);
		});
}
