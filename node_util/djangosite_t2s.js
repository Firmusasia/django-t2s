#!/usr/bin/env node

var argv = require('minimist')(process.argv.slice(2));
var Opencc = require('opencc');
var configName = 't2s';
if (argv.config)
  configName = argv.config;

(new Opencc(configName + '.json')).convert(argv._.join(' '),
  function(err, output) {
    if (err)
      throw err;
    process.stdout.write(output);
  });
