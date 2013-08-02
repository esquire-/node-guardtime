# Guardtime Node.js API Documentation

This module provides bindings to the Guardtime API. It acts as a wrapper around the Guardtime C Library.

This module is split into two classes:

* `TimeSignature` encapsulates the signature token. It offers some low-level 'static' methods.
* `GuardTime` is a service layer class that bridges these signature tokens to GuardTime services.

# Contents
* [Basic Usage](#basic_usage)
* [Module Guardtime](#module_guardtime)
  * [Guardtime](#guardtime)
  * [`guardtime.conf(properties)`](#guardtime.conf)
  * [`guardtime.sign(String data, function(Exception err, TimeSignature ts))`](#guardtime.sign)
  * [`guardtime.signFile(String filename, function(Exception err, TimeSignature ts))`](#guardtime.signfile)
  * [`guardtime.signHash(binary_hash, String hashalgorithm, function(Exception err, TimeSignature ts))`](#guardtime.signhash)
  * [`guardtime.save(String filename, TimeSignature ts, function(Exception err))`](#guardtime.save)
  * [`guardtime.load(String filename, function(Exception err, TimeSignature ts))`](#guardtime.load)
  * [`TimeSignature ts = guardtime.loadSync(String filename)`](#guardtime.loadsync)
  * [`guardtime.verify(String data, TimeSignature ts, function(Exception err, Integer resultflags, properties))`](#guardtime.verify)
  * [`guardtime.verifyFile(String filename, TimeSignature ts, function(Exception err, Integer resultflags, properties))`](#guardtime.verifyfile)
  * [`guardtime.verifyHash(binary_hash, String hashalgorithm, TimeSignature ts, function(Exception err, Integer resultflags, properties))`](#guardtime.verifyhash)
    * [Result Flags](#result_flags)
  * [`guardtime.loadPublications(function(Exception err))`](#guardtime.loadpublications)
  * [`guardtime.extend(TimeSignature ts, function(Exception err, TimeSignature ts))`](#guardtime.extend)
* [Module TimeSignature](#module_timesignature)
  * [TimeSignature(der\_token\_content)](#timesignature)
  * [`Buffer request = timesignature.composeExtendingRequest()`](#timesignature.composeextendingrequest)
  * [`Object signature_properties = timesignature.verify()`](#timesignature.verify)
  * [`Boolean earlier = timesignature.isEarlierThan(TimeSignature ts2)`](#timesignature.isearlierthan)
  * [`Date date = timesignature.getRegisteredTime()`](#timesignature.getregisteredtime)
  * [`String s = timesignature.getSignerName()`](#timesignature.getsignername)
  * [`Boolean extended = timesignature.isExtended()`](#timesignature.isextended)
  * [`String algo_name = timesignature.getHashAlgorithm()`](#timesignature.gethashalgorithm)
  * [`Integer checks_done = timesignature.verifyHash(hash, String algo)`](#timesignature.verifyhash)
  * [`Buffer data_blob = timesignature.getContent()`](#timesignature.getcontent)
  * [`Boolean ok = timesignature.extend(response)`](#timesignature.extend)
  * ['static' functions for internal use](#static_functions)

<h2 id="basic_usage">Basic Usage:</h2>

    var gt = require('guardtime');
    
    gt.conf({ signeruri: 'http://my.gateway/gt-signingservice',
    verifieruri: 'http://my.gateway/gt-extendingservice'});

    gt.sign('some data', function(error, token) {
      if(error)
        throw error;
      console.log('Very secure time: ', token.getRegisteredTime());
      gt.verify('some data', token, function(error, checkflags, properties) {
        if (error)
          throw error;
        console.log('Signature OK, signed by ' + properties.location_name);
      })
    });

TimeSignature is exported as `guardtime.TimeSignature`. If you need to store and retrieve the TimeSignature token then use something like:

    arbitraryDatabase.putBlob(id, token.getContent());
    retrievedToken = new guardtime.TimeSignature(arbitraryDatabase.getBlob(id));

<h2 id="module_guardtime">Module Guardtime</h2>

<h3 id="guardtime">Guardtime</h3>

The Guardtime module offers access to Guardtime signature and transport utilities.

Use `var guardtime = require('guardtime');` to access this class.

<h3 id="guardtime.conf"><tt>guardtime.conf(properties)</tt></h3>
Optionally change the service configuration, all parameters are optional.

Default Values:

    gt.conf({
      signeruri: 'http://stamper.guardtime.net/gt-signingservice',       // or replace with private Gateway address
          verifieruri: 'http://verifier.guardtime.net/gt-extendingservice',  // or replace with private Gateway address
          publicationsuri: 'http://verify.guardtime.com/gt-controlpublications.bin',  // ok for most scenarios
          publicationsdata: ''              // automatically loaded from publicationsuri if blank or expired
          publicationslifetime: 60*60*7     // seconds; if publicationsdata is older then it will be reloaded
    });

<h3 id="guardtime.sign"><tt>guardtime.sign(String data, function(Exception err, TimeSignature ts))</tt></h3>
Signs the given data String, returning a TimeSignature and an exception to the callback function.
The exception is null if no errors were encountered.

Example:

    var data = "Hello, world!";
    guardtime.sign(data, function(err, token) {
      if(err)
        throw err;
      console.log('Signed at ' + token.getRegisteredTime());
      //Must now record the token
    });

<h3 id="guardtime.signfile"><tt>guardtime.signFile(String filename, function(Exception err, TimeSignature ts))</tt></h3>
Calculates the hash (using SHA256) of the given file and signs it, returning a TimeSignature and an exception to the callback function.
The exception is null if no errors were encountered.

Example:

    var file = "/path/to/file.extension";
    guardtime.signFile(file, function(err, token) {
      if(err)
        throw err;
      console.log('Signed at ' + token.getRegisteredTime());
      //Must now record the token
    });

<h3 id="guardtime.signhash"><tt>guardtime.signHash(binary_hash, String hashalgorithm, function(Exception err, TimeSignature ts))</tt></h3>
Signs the hash provided as a Buffer or a String, using the String hashalgorithm to determine the hashing algorithm. Hash algorithm names are OpenSSL standard names. Returns a TimeSignature and an exception to the callback function. The exception is null if no errors were encountered.

Example:

    var hash = getHash();
    guardtime.signHash(hash, 'SHA256', function(err, token) {
      if(err)
        throw err;
      console.log('Signed at ' + token.getRegistrationTime());
      //Must now record the token
    });

<h3 id="guardtime.save"><tt>guardtime.save(String filename, TimeSignature ts, function(Exception err))</tt></h3>
Utility to save the given Time Signature to a file specified by the String filename. Asynchronous.
Passes an exception to the callback in case of an error; the exception is null if no errors were encountered.

<h3 id="guardtime.load"><tt>guardtime.load(String filename, function(Exception err, TimeSignature ts))</tt></h3>
Utility to load a Time Signature object from the file given by the String filename. Asynchronous.
Returns the TimeSignature and an error to the callback function. The exception is null if no errors were encountered.

Example:

    guardtime.load("/path/to/file", function(err, token) {
      if(err)
        throw err;
      //Now do something with token
    });

<h3 id="guardtime.loadsync"><tt>TimeSignature ts = guardtime.loadSync(String filename)</tt></h3>
Same as `guardtime.load()`, but synchronous.

Example:

    TimeSignature ts = guardtime.loadSync("/path/to/file");

<h3 id="guardtime.verify"><tt>guardtime.verify(String data, TimeSignature ts, function(Exception err, Integer resultflags, properties))</tt></h3>
Verifies the TimeSignature ts, checking against the hash of String data. The callback function is given an exception in the event of an error, an Integer containing result flags from the verification, and a properties structure containing details of the verified data. There is no need to validate the result flags as the necessary checks are hardcoded and an exception is returned in the case of an error. Possible result flags are presented below.  

<h3 id="guardtime.verifyfile"><tt>guardtime.verifyFile(String filename, TimeSignature ts, function(Exception err, Integer resultflags, properties))</tt></h3>
Verifies the TimeSignature ts, using the hash of the file given as the String filename to run the check. The callback function is given an exception in the event of an error, an Integer containing result flags from the verification, and a properties structure containing details of the verified data. There is no need to validate the result flags as the necessary checks are hardcoded and an exception is returned in the case of an error. Possible result flags are presented below.  

<h3 id="guardtime.verifyhash"><tt>guardtime.verifyHash(binary_hash, String hashalgorithm, TimeSignature ts, function(Exception err, Integer resultflags, properties))</tt></h3>
Verifies TimeSignature ts, using the Buffer or String binary_hash as the hash to be checked against. Uses the String hashalgorithm to determine how to process the hash. Callback function is given an Exception in event of an error, an Integer containing flags about the checks, and a properties structure containing the details of the verified data. There is no need to validate the result flags as the neccesary checks are hardcoded and an exception is returned in case of an error. Possible result flags are:

<h4 id="result_flags">Result Flags:</h4>

- `guardtime.VER_RES.PUBLIC_KEY_SIGNATURE_PRESENT`: Token is verified using RSA signature; newspaper publication is not yet available or accessible.
- `guardtime.VER_RES.PUBLICATION_REFERENCE_PRESENT`: Properties list includes human-readable array of newspapers or other trusted media which could be used for independent signature verification.
- `guardtime.VER_RES.DOCUMENT_HASH_CHECKED`: Document content or hash was provided and it matches the hash value in signature token. Always present.
- `guardtime.VER_RES.PUBLICATION_CHECKED`: Token is verified using trusted publication which is printed in newspapers for independent verification.

The signature properties structure is populated with the following fields:

- `verification_status` : flags about checks performed, see `resultflags` above.
- `location_id`: Numeric ID of issuing server (gateway), *trusted*.
- `location_name`: Human-readable ID of issuing server (gateway), *trusted* as it is set by upstream infrastructure and cannot be modified by gateway operatur. Formatted as a ':' separated hierarchical list of entities; UTF-8 encoding.
- `registered_time`: Date object encapsulating *trusted* signing time/date.
- `policy`: Legally binding and audited signing policy OID.
- `hash_value`, `hash_algorithm`: Hash value of original signed doc, and name of used hash algorithm.
- `issuer_name`: Name of issuing server (gateway). May be changed by the gateway itself, take it as a 'label'.
- `public_key_fingerprint`: (present if 'PUBLIC_KEY_SIGNATURE_PRESENT'). Fingerprint of certificate used to sign the token; matches with whitelist published in _publications file_. Will be superceded with newspaper publication when it becomes available.
- `publication_string`: (this and following fields present if 'PUBLICATION_CHECKED'). Publication value used to validate the token, matches with newspaper publication value.
- `publication_time`, `publication_identifier`: Date object which encapsulates publishing time; _identifier_ is same encoding as unix _time_t_ value.
- `pub_reference_list`: Human-readable pointers to trusted media which could be used to validate the _publication string_. Encoded as an array of UTF-8 strings.

*Note* that depending on data availability some fields may not be present.

<h3 id="guardtime.loadpublications"><tt>guardtime.loadPublications(function(Exception err))</tt></h3>
Loads Guardtime publications data from network and saves it in the `guardtime` object for future verification use. _Note_ that all verification functions need this data and will call this function if it is not done explicitly. It is advisable to reload the publications data every six hours.
Callback is called when loading is done, error is null if the request was successful.

<h3 id="guardtime.extend"><tt>guardtime.extend(TimeSignature ts, function(Exception err, TimeSignature ts))</tt></h3>
Creates 'extended' form of TimeSignature token, ready for hash-chain based verification. This is primarily used internally. This does not create a new TimeSignature token, it modifies the one provided.
*Note* that if the callback returns an error then signature cannot be considered broken, it could still be verified without extension.

<h2 id="module_timesignature">Module TimeSignature</h2>

<h3 id="timesignature">TimeSignature(der_token_content)</h3>

Create a new TimeSignature token from a DER-encoded serialized object representation (eg a file on disc).
Use `var timesignature = new TimeSignature(der_encoded_content);` to access this class.

<h3 id="timesignature.composeextendingrequest"><tt>Buffer request = timesignature.composeExtendingRequest()</tt></h3>
Creates a request data blob to be sent to the Verification service.

<h3 id="timesignature.verify"><tt>Object signature_properties = timesignature.verify()</tt></h3>
Verifies the internal consistency of the signature token and returns structure with signature properties. See `guardtime.verify()`. Throws an exception in case of error or 'broken' signature.

<h3 id="timesignature.isearlierthan"><tt>Boolean earlier = timesignature.isEarlierThan(TimeSignature ts2)</tt></h3>
Compares two signature tokens, returns True if encapsulated token is _provably_ older than one provided as an argument. False otherwise.

<h3 id="timesignature.getregisteredtime"><tt>Date date = timesignature.getRegisteredTime()</tt></h3>
Returns provably secure signature registration time as Date object. Resolution: 1 second.

<h3 id="timesignature.getsignername"><tt>String s = timesignature.getSignerName()</tt></h3>
Returns signer's identity as ':' delimited hierarchial list of responsible authenticators.
If the token does not contain an identity then an empty string ('') is returned.

<h3 id="timesignature.isextended"><tt>Boolean extended = timesignature.isExtended()</tt></h3>
Returns True if timesignature token has all missing bits of hash-chain embedded for offline 
verification. False otherwise.

<h3 id="timesignature.gethashalgorithm"><tt>String algo_name = timesignature.getHashAlgorithm()</tt></h3>
Returns OpenSSL-style hash algorithm name. Necessary for verification - data has to be hashed with the same algorithm for comparison.

<h3 id="timesignature.verifyhash"><tt>Integer checks_done = timesignature.verifyHash(hash, String algo)</tt></h3>
Compares given hash to hash in signature token; only valid if hash algorithms are the same.
Returns a bitfield with verification information, constructed in the same format as above.
*Note* that validation of the return value is unnecessary, it is included for historical reasons.

<h3 id="timesignature.getcontent"><tt>Buffer data_blob = timesignature.getContent()</tt></h3>
Returns serialized DER representation of TimeSignature token

<h3 id="timesignature.extend"><tt>Boolean ok = timesignature.extend(response)</tt></h3>
Creates 'extended' version of TimeSignature token by including missing bits of the hash chain.
Input: Buffer or String with verification service response; returns True or throws an Exception.

<h3 id="static_functions">'static' functions for internal use:</h3>

`Buffer request = TimeSignature.composeRequest(hash, String hashalgorithm)`
Creates request data to be sent to signing service. Input: binary hash (Buffer or String) and hash algorithm name.

`Buffer der_token_content = TimeSignature.processResponse(response)`
Creates DER encoded serialized TimeSignature, usually fed to TimeSignature constructor.
Input: response from signing service.

`Boolean ok = TimeSignature.verifyPublications(der_publications_file_content)`
Verifies publications file (this is used by a higher level verification routine).
Returns True or throws exception.
