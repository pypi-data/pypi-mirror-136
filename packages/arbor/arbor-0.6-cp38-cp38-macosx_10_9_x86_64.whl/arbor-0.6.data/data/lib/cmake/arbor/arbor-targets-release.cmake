#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "arbor::arbor" for configuration "Release"
set_property(TARGET arbor::arbor APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(arbor::arbor PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libarbor.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS arbor::arbor )
list(APPEND _IMPORT_CHECK_FILES_FOR_arbor::arbor "${_IMPORT_PREFIX}/lib/libarbor.a" )

# Import target "arbor::arborenv" for configuration "Release"
set_property(TARGET arbor::arborenv APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(arbor::arborenv PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libarborenv.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS arbor::arborenv )
list(APPEND _IMPORT_CHECK_FILES_FOR_arbor::arborenv "${_IMPORT_PREFIX}/lib/libarborenv.a" )

# Import target "arbor::arborio" for configuration "Release"
set_property(TARGET arbor::arborio APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(arbor::arborio PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libarborio.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS arbor::arborio )
list(APPEND _IMPORT_CHECK_FILES_FOR_arbor::arborio "${_IMPORT_PREFIX}/lib/libarborio.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
