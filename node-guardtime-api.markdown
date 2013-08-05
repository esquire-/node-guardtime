# Guardtime.js
__Node.js Library for the Guardtime KSI Service__

----

Guardtime.js provides a wrapper for the Guardtime C Library, allowing Node.js developers to timestamp their data with Guardtime's Keyless Signature Infrastructure. This document assumes a basic understanding of KSI, for a more detailed explanation please see the [Guardtime Website](http://www.guardtime.com/signatures/technology-overview).

----

## How Guardtime's technology works:

__This section presents a brief summary of Guardtime's KSI technology. It is by knows means complete, but should give you an understanding of concepts used in the API.__

1. You have a document, `d`. It can be a PDF, an RTF file, or a picture. Anything that can be hashed.
2. You take the hash of this document, `h`, where `h = hash(d)`.
3. You submit `h` to a Guardtime Gateway server. This server can be one of Guardtime's public servers (default) or an internal Gateway used by your organization or provider. The data, `d`, that produced `h` never needs to leave your system.
4. The Gateway processes your request and returns a _non-extended_ signature. This signature indicates details about the document, including the hash of the document and the time at which it was recorded.
5. *You* record this signature in a file or database.
6. This signature can later be verified, through a Guardtime Gateway, to have been generated at the specified time and to be directly linked to `h`, and therefore `d`, proving that `d` existed at the specified time.
7. The signature can also be extended, through a Guardtime Gateway. If it has been extended the validity of the signature can be proved using a code that Guardtime distributes [periodicallyy](https://twitter.com/GuardTime) in major publications.

----

### About Guardtime.js

Guardtime.js provides the functionality needed to generate signature requests and transmit them to a Gateway, returning signatures that can be recorded in a database or file. It makes use of the Node.js convention of providing a single callback as the last argument to an asynchronous function.

Many examples in this document assume you have a database and can insert a binary [blob](http://en.wikipedia.org/wiki/Binary_large_object) into it using a command such as 'arbitraryDb.putBlob(id, blob)' and that you can return a blob using a command such as 'arbitraryDb.getBlob(id)', where 'id' is an identifier. We also assume the arbitrary method `getToken()`, which will return a valid TimeSignature token.

----

## Basic Usage:

```javascript
var gt = require('guardtime');

var data = "The quick brown fox jumps over the lazy dog"; //Whatever you want to timestamp
var id = 5; //Some database identifier

gt.sign(data, function(err, token) {
  if(err)
    throw err;
  console.log('Recorded time: ' + token.getRegisteredTime());
  gt.verify(data, token, function(err, checkflags, properties) {
    if(err)
      throw err;
    console.log('Signature OK, signed by: ' + properties.location_name);
  });
  //Log the token to a Database
  arbitraryDb.putBlob(id, token.getContent());
});

//Retrieve the token from the database
var retrievedToken = new gt.TimeSignature(arbitraryDb.getBlob(id));
```

----

## Getting Guardtime.js

The source is available from [GitHub](https://github.com/ristik/node-guardtime).

----

## Installation

As the Guardtime Node.js Library makes use of the Guardtime C Library, the C Library must be included.

Include the Guardtime C Library in a subdirectory labeled `libgt-x.y`, where x and y are version numbers.

To build:

```shell
nmp install .
npm link
```

or

```shell
node-gyp rebuild
```

----

## Documentation

Guardtime.js has two modules - Guardtime and TimeSignature. Most developers will primarily use Guardtime and will use TimeSignature only when loading or unloading signature data from storage.

### Guardtime

* [Guardtime.js](#guardtime)
  * [conf](#conf)
  * [sign](#sign)
  * [signFile](#signfile)
  * [signHash](#signhash)
  * [verify](#verify)
  * [verifyFile](#verifyfile)
  * [verifyHash](#verifyHash)
      * [Signature Propertiess](#signature-properties)
  * [save](#save)
  * [load](#load)
  * [loadSync](#loadsync)
  * [extend](#extend)
  * [loadPublications](#loadpublications)
  * [Result Flags](#result-flags)

### Time Signature

* [Time Signature](#time-signature)
  * [TimeSignature](#timesignature)
  * [getContent](#getcontent)
  * [getRegisteredTime](#getregisteredtime)
  * [getHashAlgorithm](#gethashalgorithm)
  * [Other Functions](#other-functions)

----

<a name="guardtime" />
## Guardtime

The Guardtime module offers access to signature and transport utilities. Most developers will rely on functions from this module almost exclusively.

Include this module in your code with:

```javascript
var gt = require('guardtime');
```
----

<a name="conf" />
### conf(configuration)

Allows for the use of a custom URI as the Gateway. The defaults are sufficient for general use. This value should be updated if you are using an internal Gateway.

__Arguments__

* configuration - Object containing fields specifying Gateway URI and publications lifetime. Fields are:
  * `signeruri` - Address of the Signing service
  * `verifieruri` - Address of the Extending service
  * `publicationsuri` - Address from which to download the publications file
  * `publicationsdata` - This is used internally and is automatically loaded if empty or expired
  * `publicationslifetime` - Number of seconds before we reload the publications file, default is 7 hours

__Example__

```javascript
//These are the default values
gt.conf({
  signeruri: 'http://stamper.guardtime.net/gt-signingservice', // or replace with private Gateway address
  verifieruri: 'http://verifier.guardtime.net/gt-extendingservice', // or replace with private Gateway address
  publicationsuri: 'http://verify.guardtime.com/gt-controlpublications.bin', // ok for most scenarios
  publicationsdata: '', // automatically loaded from publicationsuri if blank or expired
  publicationslifetime: 60*60*7 // seconds; if publicationsdata is older then it will be reloaded
});
```

----

<a name="sign" />
### sign(string, callback)

Signs the provided string. This will automatically calculate the hash of the provided string, using SHA256 as the hash algorithm. It will then send this hash to the Guardtime Signer, which will return a signature token. The signature token is passed to the callback function. This method is the complement of [verify()](#verify).

__Arguments__

* string - The string of data to be signed
* callback(err, token) - Called upon completion or in the event of an error. token is a TimeSignature object.

__Example__

```javascript
var data = "Hello, world";
gt.sign(data, function(err, token) {
  if(err)
    throw err;
  console.log('Signed at ' + token.getRegisteredTime());
  //Record the token
  arbitraryDb.putBlob(id, token.getContent());
});
```

----

<a name="signfile" />
### signFile(file, callback)

Similar to [sign()](#sign), except that this function calculates the hash of a file instead of a string. Uses SHA256 as the hash algorithm. It will then send this hash to the Guardtime Signer, which will return a signature token. The signature token is passed to the callback function. This method is the complement of [verifyFile()](#verifyfile).

__Arguments__

* file - String indicating the location of the file to be hashed
* callback(err, token) - Called upon completion or in the event of an error. 'token' is a TimeSignature object.

__Example__

```javascript
gt.signFile('/path/to/file', function(err, token) {
  if(err)
    throw err;
  console.log('Signed at ' + token.getRegisteredTime());
  //Record the token
  arbitraryDb.putBlob(id, token.getContent());
});
```

----

<a name="signhash" />
### signHash(hash, algorithm, callback)

Signs the given hash, using the specified hash algorithm. It will then send this hash to the Guardtime Signer, which will return a signature token. The signature token is passed to the callback function. This method is the complement of [verifyHash()](#verifyhash).

__Arguments__

* hash - Buffer or String containing the hash value of the data to be signed.
* algorithm - A string representing the algorithm that was used to sign the data. This must be correct or the signature may fail to validate in the future. Uses OpenSSL-style hash names.
* callback(err, token) - Called upon completion or in the event of an error. token is a TimeSignature object.

__Example__

```javascript
var data = 'Hello, world';
var hash = SomeHashFunction(data, 'SHA256'); //Some method of hashing.
gt.signHash(hash, 'SHA256', function(err, token) {
  if(err)
    throw err;
  console.log('Signed at ' + token.getRegisteredTime());
  //Record the token
  arbitraryDb.putBlob(id, token.getContent());
});
```

----

<a name="verify" />
### verify(string, token, callback)

This method verifies the given string against the given token, passing results to the callback function. This is the complement to [sign()](#sign).

__Arguments__

* string - A string containing data which will be hashed using SHA256 and compared against the token.
* token - The TimeSignature token generated when the data was originally signed.
* callback(err, result, properties) - Called upon completion or in the event of an error. 'result' is an integer assembled from a bitfield. Its fields are [included](#result-flags) in this document, but they do not need to be validated as an error will return an exception. 'properties' contains the data returned during the verification. Its fields are [below](#signature-properties).

__Example__

```javascript
var string = 'Hello, world';
var token = new gt.TimeSignature(arbitraryDb.getBlob(id));
gt.verify(string, token, function(err, result, properties) {
  if(err)
    throw err;
  console.log('Signed by ' + properties.location_id + ' at ' + properties.registered_time);
  //A full list of property values is included in this document
});
```

----

<a name="verifyFile" />
### verifyFile(file, token, callback)

This method verifies the given file against the given token, passing results to the callback function. This is the complement of [signFile()](#signfile).

__Arguments__

* file - A string indicating the location of the file to be hashed.
* token - The TimeSignature token generated when the data was successfully signed.
* callback(err, result, properties) - Called upon completion or in the event of an error. 'result' is an integer assembled from a bitfield. Its fields are [included](#result-flags) in this document, but they do not need to be validated as an error will return an exception. 'properties' contains the data returned during the verification. Its fields are [below](#signature-properties).

__Example__

```javascript
var token = new gt.TimeSignature(arbitraryDb.getBlob(id));
gt.verifyFile('/path/to/file', token, function(err, result, properties) {
  if(err)
    throw err;
  console.log('Signed by ' + properties.location_id + ' at ' + properties.registered_time);
  //A full list of property values is included in this document
});
```

----

<a name="verifyhash" />
### verifyHash(hash, algorithm, token, callback)

This method verifies the given hash against the given token, passing results to the callback function. This is the complement of [signHash()](#signhash).

__Arguments__

* hash - Buffer containing the hash value of the data to be signed.
* algorithm - A string representing the algorithm that was used to sign the data. This must be correct or the signature may fail to validate in the future. Uses OpenSSL-style hash names.
* callback(err, result, properties) - Called upon completion or in the event of an error. 'result' is an integer assembled from a bitfield. Its fields are [included](#result-flags) in this document, but they do not need to be validated as an error will return an exception. 'properties' contains the data returned during the verification. Its fields are [below](#signature-properties).

__Example__

```javascript
var data = 'Hello, world';
var hash = SomeHashFunction(data, 'SHA256'); //Some method of hashing.
var token = new gt.TimeSignature(arbitraryDb.getBlob(id));

gt.verifyHash(hash, token, token.getHashAlgorithm(), function(err, result, properties) {
  if(err)
    throw err;
  console.log('Signed by ' + properties.location_id + ' at ' + properties.registered_time);
  //A full list of property values is included in this document
});
```

----

<a name="signature-properties" />
#### Signature Properties:

- `verification_status` : flags about checks performed, see `resultflags` below.
- `location_id`: Numeric ID of issuing server (gateway), *trusted*.
- `location_name`: Human-readable ID of issuing server (gateway), *trusted* as it is set by upstream infrastructure and cannot be modified by gateway operator. Formatted as a ':' separated hierarchical list of entities; UTF-8 encoding.
- `registered_time`: Date object encapsulating *trusted* signing time/date.
- `policy`: Legally binding and audited signing policy OID.
- `hash_value`, `hash_algorithm`: Hash value of original signed doc, and name of used hash algorithm.
- `issuer_name`: Name of issuing server (gateway). May be changed by the gateway itself, take it as a 'label'.
- `public_key_fingerprint`: (present if 'PUBLIC_KEY_SIGNATURE_PRESENT'). Fingerprint of certificate used to sign the token; matches with whitelist published in _publications file_. Will be superseded with newspaper publication when it becomes available.
- `publication_string`: (this and following fields present if 'PUBLICATION_CHECKED'). Publication value used to validate the token, matches with newspaper publication value.
- `publication_time`, `publication_identifier`: Date object which encapsulates publishing time; _identifier_ is same encoding as Unix _time_t_ value.
- `pub_reference_list`: Human-readable pointers to trusted media which could be used to validate the _publication string_. Encoded as an array of UTF-8 strings.

**Note** that depending on data availability some fields may not be present.

----

<a name="save" />
### save(file, token, callback)

This is a simple utility to save a token to disk. It extracts necessary data from a token and writes it out to the specified file. Note that if the given file already exists it may be overwritten. This method is asynchronous. It is the complement of [load()](#load).

__Arguments__

* file - A string indicating the location where the token should be saved.
* token - The TimeSignature token to be written to disc.
* callback(err) - Called upon completion or in the event of an error.

__Example__

```javascript
var token = getToken(); //Get a token

gt.save('/path/to/file', token, function(err) {
  if(err)
    throw err;
});
```

----

<a name="load" />
### load(file, callback)

This is the complement of [save()](#save). It will load a token from the specified file and return it to the callback function. This method is asynchronous.

__Arguments__

* file - A string indicating the location of a signature file.
* callback(err, token) - Called upon completion or in the event of an error. 'token' is a TimeSignature object containing the signature token.

__Example__

```javascript
gt.load('/path/to/file', function(err, token) {
  if(err)
    throw err;
  gt.verify('Hello, world', token, function(err, result, properties) {
    if(err)
      throw err;
    console.log('Signed at: ' + properties.registered_time);
  });
});
```

----

<a name="loadsync" />
### loadSync(file)

This loads a token from a file *synchronously*. The TimeSignature token is returned by the function itself and is not passed to a callback.

__Arguments__

* file - A string indicating the location of the file to be loaded.

__Return__

* TimeSignature token - The TimeSignature token from that file.

__Throws__

* Exception - in the event of an error.

__Example__

```javascript
var token = gt.loadSync('/path/to/file');
```

----

<a name="extend" />
### extend(token, callback)

This function extends a given signature. It is primarily used internally and is called automatically when a signature is verified. A developer should generally not need to call this function directly.

__Arguments__

* token - The TimeSignature to be extended
* callback(err, token) - Returns the original token, not a new one. Note that an error does not necessarily mean that the signature is broken.

----

<a name="loadpublications" />
### loadPublications(callback)

This function loads or updates the publications file. This function is used internally. It is rare that a developer needs to call this directly, as it is called automatically in the event of an empty or expired publications file. 

__Arguments__

* callback(err) - Function to be called upon completion or in the event of an error.

----

<a name="result-flags" />
#### Result Flags

The following flags are present in callbacks from a [verify()](#verify) function. They are loaded as a bit field. Most developers will not need to consider these, they are checked automatically. The information here is also present in the 'properties' field of the callback. These are included primarily for backwards compatibility.

- `gt.VER_RES.PUBLIC_KEY_SIGNATURE_PRESENT`: Token is verified using RSA signature; newspaper publication is not yet available or accessible.
- `gt.VER_RES.PUBLICATION_REFERENCE_PRESENT`: Properties list includes human-readable array of newspapers or other trusted media which could be used for independent signature verification.
- `gt.VER_RES.DOCUMENT_HASH_CHECKED`: Document content or hash was provided and it matches the hash value in signature token. Always present.
- `gt.VER_RES.PUBLICATION_CHECKED`: Token is verified using trusted publication which is printed in newspapers for independent verification.

----

<a name="time-signature" />
## Time Signature

The Time Signature module stores information about a hash signature. The following methods will be useful to developers:

---

<a name="timesignature" />
### TimeSignature(context)

Constructs a new TimeSignature from a binary blob, such as a blob retrieved from a database.

__Arguments__

* context - A binary blob, such as a blob from a database. This blob can be generated with [getContent()](#getcontent).

__Return__

* TimeSignature token - The TimeSignature token contained in the binary data.

__Example__

```javascript
var blob = arbitraryDb.getBlob(id);
var token = new gt.TimeSignature(blob);
```

---

<a name="getcontent" />
### getContent()

Returns the binary content of the time signature. Useful when placing a signature into a database.

__Return__

* Buffer buffer - The binary representation of the token.

__Example__

```javascript
var token = getToken(); //Get a token
var blob = token.getContent();
arbitraryDb.putBlob(id, blob);
```

---

<a name="getregisteredtime" />
### getRegisteredTime()

Returns a Date object containing the time at which the token was registered. Useful if you need to check when a token was registered without calling verify.

__Return__

* Date registered_time - The date & time at which the object was registered.

__Example__

```javascript
var token = getToken(); //Get a token
var date = token.getRegisteredTime();
console.log('Signed at: ' + date);
```

----

<a name="gethashalgorithm" />
### getHashAlgorithm()

Returns the name of the hash algorithm that was used to create the data in this token. The hash algorithm name is useful with functions such as [gt.verifyHash()](#verifyhash).

__Return__

* String hash_algorithm - The name of the algorithm that was used to create the hash in this token.

__Example__

```javascript
var token = getToken(); //Get a token
var algo = token.getHashAlgorithm();
console.log('Token generated using algorithm: ' + algo);
```

----

<a name="other-functions" />
### Other Functions

The following functions are internal to TimeSignature and are used by the Guardtime API. A developer should not have to call them directly. They are included here for completeness.

---

###### `Buffer request = timesignature.composeExtendingRequest()`
Creates a request data blob to be sent to the Verification service.

###### `Object signature_properties = timesignature.verify()`
Verifies the internal consistency of the signature token and returns structure with signature properties. See `guardtime.verify()`. Throws an exception in case of error or 'broken' signature.

###### `Boolean earlier = timesignature.isEarlierThan(TimeSignature ts2)`
Compares two signature tokens, returns True if encapsulated token is _provably_ older than one provided as an argument. False otherwise.

###### `String s = timesignature.getSignerName()`
Returns signer's identity as ':' delimited hierarchial list of responsible authenticators.
If the token does not contain an identity then an empty string ('') is returned.

###### `Boolean extended = timesignature.isExtended()`
Returns True if timesignature token has all missing bits of hash-chain embedded for offline 
verification. False otherwise.

###### `Integer checks_done = timesignature.verifyHash(hash, String algo)`
Compares given hash to hash in signature token; only valid if hash algorithms are the same.
Returns a bitfield with verification information, constructed in the same format as above.
*Note* that validation of the return value is unnecessary, it is included for historical reasons.

###### `Boolean ok = timesignature.extend(response)`
Creates 'extended' version of TimeSignature token by including missing bits of the hash chain.
Input: Buffer or String with verification service response; returns True or throws an Exception.

###### 'static' functions for internal use:

`Buffer request = TimeSignature.composeRequest(hash, String hashalgorithm)`
Creates request data to be sent to signing service. Input: binary hash (Buffer or String) and hash algorithm name.

`Buffer der_token_content = TimeSignature.processResponse(response)`
Creates DER encoded serialized TimeSignature, usually fed to TimeSignature constructor.
Input: response from signing service.

`Boolean ok = TimeSignature.verifyPublications(der_publications_file_content)`
Verifies publications file (this is used by a higher level verification routine).
Returns True or throws exception.
