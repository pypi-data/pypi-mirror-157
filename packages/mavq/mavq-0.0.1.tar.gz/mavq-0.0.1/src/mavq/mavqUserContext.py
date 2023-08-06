from tomlkit import datetime
import time
from commonProvider import OBJECT_TYPE, PLATFORM_SERVICES
import jwt

"""
MavQUserContext provide the context with supported various functionality to login in user

@since 20-May-2022
@author Vishal Agarwal
@access public
"""
class MavQUserContext:

    """
    @param {String} accessToken - Access token
    @param {String} userUri - User Resource Uri
    @param {String} password - Using just for regenerate the Access token if expire.
    @param {MavQPlatformClient} clientContext - Client context
    
    @example new MavQUserContext('TOKEN', 'mavq:core://tenants/admin/users/system-administrator', 'xyz', clientContext)
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    """
    def __init__(self, clientContext, accessToken = '', userUri = '', password = ''):
        self.accessToken = accessToken
        self.clientContext = clientContext
        self.userUri = userUri
        self.userPass = password

    """
    Provide a support to perform the any Request to mavQ Platform
    @param {String} requestMethod - Request Method like `get, post` etc
    @param {String} requestUrl - Request Url
    @param {Object} requestBody - Request body
    @param {Object} additionalHeaders - Additional headers apart from default one. Also override the default by it.
    @param {Object} requestQuerystring - Query params
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return Response of request
    """
    def performRequest(self, requestMethod, requestUrl = '', requestBody = {}, additionalHeaders = {}, requestQuerystring = {}):
        self.validateAndReassignAccessToken()
        return {
            "method": requestMethod,
            "url": requestUrl,
            "headers": {"Authorization": "Bearer {}".format(self.accessToken), "Content-Type": "application/json"} + additionalHeaders,
            "data": requestBody,
            "params": requestQuerystring
        }
  
    """
    Provide a support to perform the operation to mavQ Platform

    @param {PLATFORM_SERVICES} service - MavQ Platform Service like `CORE, DATA` etc
    @param {Object} operationData - Request body for operation
    @param {Object} additionalHeaders - Additional headers apart from default one. Also override the default by it.
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return Response of request
    """
    def performOperation(self, service = PLATFORM_SERVICES.CORE, operationData = {}, additionalHeaders = {}):
        operationUrl = 'v1/tenants/' + self.clientContext.getTenantName() + '/operations/'
        requestUrl = self.getBaseUrlByService(service)
        if(requestUrl.endswith('/')):
            requestUrl += operationUrl
        else:
            requestUrl = requestUrl + '/' + operationUrl
        return self.performRequest('post', requestUrl, operationData, additionalHeaders, {})
    
    """
    
    Provide a service url of mavQ Platform

    @param {String} service - MavQ Platform Service like `CORE, DATA` etc
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access public
    
    @return {String} Return the service url
    """
    def getBaseUrlByService(self, service):
        if(service.upper() == PLATFORM_SERVICES.CORE):
            return self.clientContext.getCoreServiceBaseUrl()
        elif(service.upper() == PLATFORM_SERVICES.DATA):
            return self.clientContext.getDataServiceBaseUrl()
        elif(service.upper() == PLATFORM_SERVICES.OBJECTS):
            return self.clientContext.getObjectServiceBaseUrl()
        else:
            raise Exception("Platform does not support given {service}, Supported services {services}".format(service=service.upper(), services=', '.join(PLATFORM_SERVICES.keys())))
    
    """
    Validate that given access token expire or not, If it's expire or about to expire then generate new token
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access private
    """
    def validateAndReassignAccessToken(self):
        tokenData = jwt.decode(self.accessToken)
        minuteDiff = datetime.datetime.fromtimestamp(tokenData.exp * 1000).getTime() - time.time()//60000
        if (minuteDiff <= 30):
            self.accessToken = self.clientContext.loginAndGetTokenOnly(self.userUri, self.userPass)

    """
    Create the object record on object service
    
    @param {OBJECT_TYPE} type - Object type like SQL, NOSQL
    @param {String} objectConfigurationId - Object Configuration Id
    @param {Object} requestBody - Request Body
    @param {Object} additionalHeader - Additional Header
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access Public
    
    @return {Axios<Response>} Response of request
    """
    def createRecord(self, objectConfigurationId, objectType = OBJECT_TYPE.SQL, requestBody = {}, additionalHeader = {}):
        return self.performRequest(
            'post',
            self.prepareObjectRecordUrlByType(objectType, objectConfigurationId),
            requestBody,
            additionalHeader
        )
    
    
    """
    Search the object record on object service

    @param {OBJECT_TYPE} type - Object type like SQL, NOSQL
    @param {String} objectConfigurationId - Object Configuration Id
    @param {Object} requestBody - Request Body
    @param {Object} additionalHeader - Additional Header
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access Public
    
    @return Response of request
    """
    def searchRecords(self, objectConfigurationId, objectType = OBJECT_TYPE.SQL, requestBody = {}, additionalHeader = {}):
        return self.performRequest(
            'post',
            self.prepareObjectRecordUrlByType(objectType, objectConfigurationId) + 'search/',
            requestBody,
            additionalHeader
        )
    
    """
    Get Specific object record from object service
    
    @param {OBJECT_TYPE} type - Object type like SQL, NOSQL
    @param {String} objectConfigurationId - Object Configuration Id
    @param {String} objectRecordId - Object Record Id
    @param {Object} additionalHeader - Additional Header
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access Public
    
    @return  Response of request
    """
    def getRecordById(self, objectConfigurationId, objectType = OBJECT_TYPE.SQL, objectRecordId = '', additionalHeader = {}):
        return self.performRequest(
            'get',
            self.prepareObjectRecordUrlByType(objectType, objectConfigurationId) + str(objectRecordId) + "/",
            {},
            additionalHeader
        )
    
    """
    Update Specific record on object service
    
    @param {OBJECT_TYPE} type - Object type like SQL, NOSQL
    @param {String} objectConfigurationId - Object Configuration Id
    @param {String} objectRecordId - Object Record Id
    @param {Object} requestBody - Request body
    @param {Object} additionalHeader - Additional Header
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access Public
    
    @return {Axios<Response>} Response of request
    """
    def updateRecordById(self, objectConfigurationId, objectType = OBJECT_TYPE.SQL, objectRecordId = '', requestBody ={}, additionalHeader = {}):
        return self.performRequest(
            'put',
            self.prepareObjectRecordUrlByType(objectType, objectConfigurationId) + str(objectRecordId) + "/",
            requestBody,
            additionalHeader
        )
    
    """
    Delete Specific object record from object service
    
    @param {OBJECT_TYPE} type - Object type like SQL, NOSQL
    @param {String} objectConfigurationId - Object Configuration Id
    @param {String} objectRecordId - Object Record Id
    @param {Object} additionalHeader - Additional Header
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access Public
    
    @return {Axios<Response>} Response of request
    """
    def deleteRecordById(self, objectConfigurationId, objectType = OBJECT_TYPE.SQL, objectRecordId = '', additionalHeader = {}):
        return self.performRequest(
            'delete',
            self.prepareObjectRecordUrlByType(objectType, objectConfigurationId) + str(objectRecordId) + '/',
            {},
            additionalHeader
        )
    
    """
    Prepare Object record url by object type
    
    @param {OBJECT_TYPE} type - Object type like SQL, NOSQL
    @param {String} objectConfigurationId - Object configuration Id
    
    @since 20-May-2022
    @author Vishal Agarwal
    @access Private
    
    @return {String} Return the service url
    """
    def prepareObjectRecordUrlByType(self, objectType = OBJECT_TYPE.SQL, objectConfigurationId = ''):
        requestUrl = self.clientContext.getObjectServiceBaseUrl()
        if (not requestUrl.endsWith('/')):
            requestUrl += '/'
        return '{requestUrl}v1/tenants/{tenant}/object_manager/{objectType}/{objectConfigurationId}/'.format(requestUrl=requestUrl, tenant=self.clientContext.getTenantName(), objectType=objectType, objectConfigurationId=objectConfigurationId)
