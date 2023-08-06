from automationVariables import OBJECT_CREATE, OBJECT_UPDATE, FIELD_CREATE, FIELD_UPDATE, FIELD_SEARCH_QUERY, LAYOUT_CREATE, LAYOUT_UPDATE, LAYOUT_SEARCH_QUERY, RECORDTYPE_CREATE, RECORDTYPE_UPDATE, RECORDTYPE_SEARCH_QUERY, RECORD_CREATE, RECORD_UPDATE, RECORD_SEARCH_QUERY
from mavqPlatformClient import mavqPlatformClient

class AutomationClient:

    def __init__(self, mavqClient, objectId="pythonObject", objectName="complaints", fieldId="abcprojects-emailfield", layoutId="abcprojects-pythonlayout", recordTypeId = "abcprojects-pythonrectype", recordId = "ue1042001-8341-4201-9d54-e466f9df9dd7"):
        self.__objectId = objectId
        self.__objectName = objectName
        self.__fieldId = fieldId
        self.__layoutId = layoutId
        self.__recordId = recordId
        self.__mavqClient = mavqClient
        self.__recordTypeId = recordTypeId

    def __createObject(self):
        print(self.__mavqClient.createObject(OBJECT_CREATE).content)
    
    def __updateObject(self):
        print(self.__mavqClient.updateObject(OBJECT_UPDATE, self.__objectId).content)
    
    def __createField(self):
        print(self.__mavqClient.createObjectField(FIELD_CREATE).content)
    
    def __updateField(self):
        print(self.__mavqClient.updateObjectField(FIELD_UPDATE, self.__fieldId).content)
    
    def __getFields(self):
        print(self.__mavqClient.getObjectFields(FIELD_SEARCH_QUERY).content)
    
    def __deleteField(self):
        print(self.__mavqClient.deleteObjectField(self.__fieldId).content)
    
    def __createLayout(self):
        print(self.__mavqClient.createObjectLayout(LAYOUT_CREATE).content)
    
    def __updateLayout(self):
        print(self.__mavqClient.updateObjectLayout(LAYOUT_UPDATE, self.__layoutId).content)

    def __getLayouts(self):
        print(self.__mavqClient.getObjectLayouts(LAYOUT_SEARCH_QUERY).content)
    
    def __createRecordType(self):
        print(self.__mavqClient.createObjectRecordType(RECORDTYPE_CREATE).content)
    
    def __updateRecordType(self):
        print(self.__mavqClient.updateObjectRecordType(RECORDTYPE_UPDATE, self.__recordTypeId).content)
    
    def __getRecordTypes(self):
        print(self.__mavqClient.getObjectRecordTypes(RECORDTYPE_SEARCH_QUERY).content)
    
    def __createRecord(self):
        print(self.__mavqClient.createObjectRecord(RECORD_CREATE, self.__objectName).content)

    def __updateRecord(self):
        print(self.__mavqClient.updateObjectRecord(RECORD_UPDATE, self.__objectName, self.__recordId).content)
    
    def __searchRecords(self):
        print(self.__mavqClient.searchObjectRecords(RECORD_SEARCH_QUERY, self.__objectName).content)
    
    def __deleteRecord(self):
        print(self.__mavqClient.deleteObjectRecord(self.__objectName, self.__recordId).content)
    
    def __deleteObject(self):
        print(self.__mavqClient.deleteObject(self.__objectId).content)
    
    def automate(self):
        print("Creating Object --------------------------------")
        self.__createObject()
        print("Updating Object --------------------------------")
        self.__updateObject()
        print("Creating Field --------------------------------")
        self.__createField()
        print("Updating Field --------------------------------")
        self.__updateField()
        print("Fetching Fields --------------------------------")
        self.__getFields()
        print("Delete Field --------------------------------")
        self.__deleteField()
        print("Creating Layout --------------------------------")
        self.__createLayout()
        print("Updating Layout --------------------------------")
        self.__updateLayout()
        print("Fetch Layouts --------------------------------")
        self.__getLayouts()
        print("Creating Record Type --------------------------------")
        self.__createRecordType()
        print("Updating Record Type --------------------------------")
        self.__updateRecordType()
        print("Fetching Record Type --------------------------------")
        self.__getRecordTypes()
        print("Creating Record --------------------------------")
        self.__createRecord()
        print("Updating Record --------------------------------")
        self.__updateRecord()
        print("Fetch Records --------------------------------")
        self.__searchRecords()
        print("Delete Record --------------------------------")
        self.__deleteRecord()
        print("Delete Object --------------------------------")
        self.__deleteObject()

mavqClient = mavqPlatformClient("admin", "https://core-api-dev.internal.mavq.io", "https://objects-api-dev.internal.mavq.io", "https://data.mavq.io", "https://auth.mavq.com", "login")
mavqClient.loginAndGetTokenOnly("mavq:core://tenants/admin/users/vishal-agarwal-back", "sG1t65RBc5")
automationClient = AutomationClient(mavqClient)
automationClient.automate()