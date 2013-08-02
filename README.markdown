# Node.js API for Guardtime Services

## Usage:

Include Guardtime C API in subdirectory `libgt-x.y`, where x and y are major and minor version numbers.

To build:

    npm install .
    npm link

or

    node-gyp rebuild

Hello world with Guardtime:

```node
  var gt = require('guardtime');

  gt.sign('Hello world!', function(err, ts) {
    if (err)
      throw err;
    gt.verify('Hello world!', ts, function(err, checkflags, props){
      if (err) 
        throw err;
      console.log('All ok; signed by ' + props.location_name + ' at ' + props.registered_time);
    });
  });
```

For API documentation please refer to the [API Documentation](https://github.com/esquire-/node-guardtime/blob/master/node-guardtime-api.markdown)

## Compatability
Requires Node.js >= 0.6.0

This software has not been tested with Windows

## What is Guardtime?

Guardtime offers a web-scale digital signature system for electronic data that uses only hash function based cryptography, creating a Keyless Signature Infrastructure. The main innovations are a distributed delivery infrastructure, which is designed for scale, and the removal of the need to rely on cryptographic keys for signature verification.

Keyless Signatures are a combination of hash function based server-side signatures and hash-linking based digital timestamping, delivered using a distributed and hierarchical infrastructure. The digital timestamp component of the service is officially certified and Guardtime is accredited as a signature authority by the European Union.

For more information, please see the [Guardtime Technology Overview](http://www.guardtime.com/signatures/technology-overview)

---
Published under Apache license v. 2.0.

Copyright GuardTime AS 2010-2013