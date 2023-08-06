#pragma once

namespace arb {
extern const char* source_id;
extern const char* arch;
extern const char* build_config;
extern const char* version;
extern const char* full_build_id;
constexpr int version_major = 0;
constexpr int version_minor = 6;
constexpr int version_patch = 0;
extern const char* version_dev;
}

#define ARB_SOURCE_ID "2022-01-26T16:08:09+01:00 1779ca77dcdf207631391e11f464837b5a2e274b"
#define ARB_ARCH "none"
#define ARB_BUILD_CONFIG "RELEASE"
#define ARB_FULL_BUILD_ID "source_id=2022-01-26T16:08:09+01:00 1779ca77dcdf207631391e11f464837b5a2e274b;version=0.6;arch=none;config=RELEASE;NEUROML_ENABLED;BUNDLED_ENABLED;"
#define ARB_VERSION "0.6"
#define ARB_VERSION_MAJOR 0
#define ARB_VERSION_MINOR 6
#define ARB_VERSION_PATCH 0
#define ARB_NEUROML_ENABLED
#define ARB_BUNDLED_ENABLED
