{
  'targets': [
    {
      'target_name': 'libsodium',
      'variables': {
        'target_arch%': '<(sodium_architecture)',
      },
      'type': 'static_library',
      'includes': [ 'sodium.gypi' ],
      'dependencies': [],
      'defines': [
        '<@(sodium_defines)',
        'SODIUM_STATIC',
        'HAVE_LIBM=1'
      ],
      'include_dirs': [
        'src/libsodium/include/sodium',
      ],
      
      'xcode_settings': {
        'OTHER_CFLAGS': [
            '-fPIC',
            '-fwrapv',
            '-fno-strict-aliasing',
            '-fstack-protector-all',
            '-Winit-self',
            '-Wwrite-strings',
            '-Wdiv-by-zero',
            '-Wmissing-braces',
            '-Wmissing-field-initializers',
            '-Wno-sign-compare',
            '-Wno-unused-const-variable',
            '-g',
            '-O2',
            '-fvisibility=hidden',
            '-Wno-missing-field-initializers',
            '-Wno-missing-braces',
            '-Wno-unused-function',
            '-Wno-strict-overflow',
            '-Wno-unknown-pragmas'
        ],
        'GCC_ENABLE_CPP_EXCEPTIONS': 'YES'
      },
      '!cflags': ['-fno-exceptions'],
      'cflags': [
        '-fexceptions',
        '-Winit-self',
        '-Wwrite-strings',
        '-Wdiv-by-zero',
        '-Wmissing-braces',
        '-Wmissing-field-initializers',
        '-Wno-sign-compare',
        '-Wno-unused-but-set-variable',
        '-g',
        '-O2',
        '-Wno-unknown-pragmas',
        '-Wno-missing-field-initializers',
        '-Wno-missing-braces'
      ],
      'ldflags': [
        '-pie',
        '-Wl',
        '-z',
        'relro'
        '-z',
        'now'
        '-Wl',
        '-z',
        'noexecstack'
      ],
      'default_configuration': 'Debug',
      'configurations': {
        'Debug': {
          'defines': [ 'DEBUG', '_DEBUG' ],
          'cflags': [ '-Wall', '-Wextra', '-O0', '-g', '-ftrapv' ],
          'msvs_settings': {
            'VCCLCompilerTool': {
              'RuntimeLibrary': 1, # static debug
            },
          },
        },
        'Release': {
          'defines': [ 'NDEBUG' ],
          'cflags': [ '-Wall', '-Wextra', '-O3' ],
          'msvs_settings': {
            'VCCLCompilerTool': {
              'RuntimeLibrary': 0, # static release
            },
          },
        }
      },
      'sources': [
        '<@(sodium_sources)'
      ]
    }
  ]
}
