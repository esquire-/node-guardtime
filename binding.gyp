{
  'targets': [
    # timesignature
    {
      'target_name': 'timesignature',
      'include_dirs': [
        'libgt-0.3.11/src/base'
      ],
      'sources': [
        'timesignature.cc'
      ],
      'dependencies': [
        'libgt-0.3.11/src/base/base.gyp:libgtbase'
      ],
      'variables': {
        # node v0.6.x doesn't give us its build variables,
        # but on Unix it was only possible to use the system OpenSSL library,
        # so default the variable to "true", v0.8.x node and up will overwrite it.
        'node_shared_openssl%': 'true',
      },
      'conditions': [
        ['node_shared_openssl=="false"', {
          # so when "node_shared_openssl" is "false", then OpenSSL has been
          # bundled into the node executable. So we need to include the same
          # header files that were used when building node.
          # non-exported directories are there to support building openssl internal
          # stuff not linked into monolithic node binary.
          'include_dirs': [
            '<(node_root_dir)/deps/openssl/openssl/include',
            '<(node_root_dir)/deps/openssl/openssl/crypto',
            '<(node_root_dir)/deps/openssl/openssl'
          ],
          'sources': [
            'openssl_missing_bits_0.8/pk7_smime.c'
          ]
        }]
      ],
    },
  ],
}
