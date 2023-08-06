
from pyrsistent import freeze

"""
Provide the base header like `content-type, accept`

@since 20-May-2022
@author Vishal Agarwal
@access public

@return {Object} - Base header
"""
BASE_HEADER_WITHOUT_AUTH = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
}

"""
Provide the base header like `content-type, accept` with Auth header `Authorization`

@since 20-May-2022
@author Vishal Agarwal
@access public

@return {Object} - Base header + `Authorization`
"""
def baseHeaderWithAuthToken(tokenWithoutBearer):
  return {'Authorization': 'Bearer {tokenWithoutBearer}'.format(tokenWithoutBearer=tokenWithoutBearer)} + BASE_HEADER_WITHOUT_AUTH


"""
Provide the `content-type: application/x-www-form-urlencoded` header

@since 20-May-2022
@author Vishal Agarwal
@access public

@return {Object} - `application/x-www-form-urlencoded` header only
"""
URLENCODED_HEADER_ONLY = {
  'Content-Type': 'application/x-www-form-urlencoded'
}

"""
Provide the constants of service name supported by mavQ Platform

@since 20-May-2022
@author Vishal Agarwal
@access public

@readonly

@return {Object} - Platform services constant
"""
PLATFORM_SERVICES = freeze({
  'CORE': 'CORE_SERVICE',
  'OBJECTS': 'OBJECTS_SERVICE',
  'DATA': 'DATA_SERVICE'
})

"""
Provide the constants of Object Type supported by mavQ Platform

@since 20-May-2022
@author Vishal Agarwal
@access public

@readonly

@return {Object} - Object Type constant
"""
OBJECT_TYPE = freeze({
  'SQL': 'sql',
  'NOSQL': 'nosql'
})