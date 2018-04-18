var program = require('commander');

program.on('--help', function(){
  console.log('  docker run --rm fluent-probe -h <FLUENT_HOST> -p <FLUENT_PORT> -l <LABEL> "<JSON STRING>"');
  console.log('');
});

program
  .version('0.1.0')
  .option('-h, --host [value]', 'Fluent host')
  .option('-p, --port [value]', 'Fluent port (default 24224)', '24224')
  .option('-l, --label [value]', 'Logger label', 'fluent-probe')
  .parse(process.argv);


var port = parseInt(program.port);
var host = program.host;

console.log('Host=%s port=%s', program.host, program.port);

var logger = require('fluent-logger')

// The 2nd argument can be omitted. Here is a default value for options.
logger.configure('tag_prefix', {
   host: program.host,
   port: program.port,
   timeout: 3.0,
   reconnectInterval: 30000 // 30 sec
});

var payload = program.args;
if (!payload) {
	payload = {'fluent-probe':'success'};
} else {
	try {
		payload = JSON.parse(payload);
	} catch(err) {
		//Ignored
	}
}

// send an event record with 'tag.label'
logger.emit(program.host, payload, function() {
	logger.close();
});