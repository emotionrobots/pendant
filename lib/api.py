#!/usr/bin/python3
#=============================================================================
#
#  api.py
#
#  ViroGuard backend API
#
#  Author: E-Motion Inc
#
#  Copyright (c) 2020-2021, E-Motion, Inc.  All Rights Researcved
#
#  License: MIT 
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#
#=============================================================================
import sys, getopt
import requests
import json
import random
import unittest


class ViroGuardApi(): 

  #---------------------------------------------------------------
  #  Initializer
  #---------------------------------------------------------------
  def __init__(self, url, cert):
    self.baseURL = url
    self.certificate = cert

  #---------------------------------------------------------------
  #
  #  registerUser(uid, name, orgs, phone, email)
  #
  #    uid - String of unique user id
  #    name - String of user name
  #    orgs - List of string, each an organizatino name
  #    phone - Phone number with country code, e.g.: +11234567890
  #    email - String of email 
  #
  #  return "Success"
  #
  #  This endpoint takes the user information provided and performs 
  #  one of two actions depending on the information provided. If no 
  #  organizations were provided, a new item is simply inserted into 
  #  the Users table with the information provided. On the other hand, 
  #  if organizations were provided, the server creates membership 
  #  items for the user for each of the organizations provided. It 
  #  then inserts a new item into the Users table using the information 
  #  provided in the request along with the memberships that it created.
  #
  #---------------------------------------------------------------
  def registerUser(self, uid, name, orgs, phone, email):
    endpt = "/userRegistration"
    req = {
      "uid": uid,
      "name": name,
      "organizations": orgs,
      "phone": phone,
      "email": email 
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  getUserInfo(uid)
  #    uid - userid
  #
  #  return {"uid":"a", 
  #          "beaconID":null, 
  #          "name":"user a", 
  #          "currentlyMemberOf":”c”, 
  #          "memberships":[
  #             {"membershipID":2,"orgID":1,"member":"a","role":"m","accepted":1},
  #             {"membershipID":3,"orgID":2,"member":"a","role":"m","accepted":0}],
  #          "cohabitants":"["b"]",
  #          "lastDailyTest”: “2021-01-01T16:20:30+01:00”,
  #          “vaccinated”:0,
  #          "profilePic":null,
  #          "phone":”+11234567890”,
  #          "email":"a@email.com",
  #          "country":null,
  #          "state":null,
  #          "city":null,
  #          "zipCode":null,
  #          “address”:null,
  #          “creditcard”:null,
  #          “provider”:null,
  #          “purchaseHistory”:null,
  #          “beaconBroadcast”:1, (1/0)
  #          “locationSharing”:1, (1/0)
  #          “audibleAlert”: 1, (1/0)
  #          “visibility”: 0 (2/1/0)
  #
  #  This endpoint queries the User table for a row with a matching 
  #  UID as the one provided as well as the Memberships table for 
  #  any memberships of that user and then returns that information.
  #
  #---------------------------------------------------------------
  def getUserInfo(self, uid):
    endpt = "/userInfo"
    req = {
      "uid": uid
    } 
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res

  #---------------------------------------------------------------
  #
  #  editUserInfo(uid, edits)
  #    uid - userid
  #    edits - list of edits, example below:
  #
  #  edits a list of {"attribute": value}; for instance:
  #    [ {“attribute”:<Attribute to change>,“value”:<Value to change to>},
  #      {“attribute”:<2nd Attribute to change>,“value”:<2nd Value to change to>},
  #	    ...,
  #    ]
  #
  #
  #  returns "Success"
  #
  #  This endpoint takes an array of attributes to edit and updates 
  #  the columns with the matching attribute names on the row with 
  #  the matching UID to the new values provided.
  #
  #---------------------------------------------------------------
  def editUserInfo(self, uid, edits):
    endpt = "/editUserInfo"
    req = {
      "uid": uid,
      "values": edits
    } 
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  addCohabitant(self, uid, email) 
  #    uid - userid
  #    email - cohabitant email  
  # 
  #  return "Success" or "Invalid Email" 
  #
  #  This endpoint checks if the provided email is a valid email of 
  #  a user. If it is, the server sends a cohabitant invite in the 
  #  form of a link to that email. If the other user accepts the 
  #  invitation by clicking the link, the two users will become 
  #  cohabitants.
  #
  #---------------------------------------------------------------
  def addCohabitant(self, uid, email): 
    endpt = "/addCohabitant"
    req = {
      "uid": uid,
      "targetEmail" : email
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  delCohabitant(self, uid, targetUid)
  #    uid - userid
  #    targetUid - cohabitant uid
  # 
  #  return "Success"
  #
  #  This endpoint uses the two UID’s provided to remove the targetUID 
  #  from the cohabitant list on the row with a matching UID.
  #
  #---------------------------------------------------------------
  def delCohabitant(self, uid, targetUid):
    endpt = "/deleteCohabitant"
    req = {
      "uid": uid,
      "targetUID" : targetUid 
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  getSocialContacts(self, uid)
  #    uid - userid
  # 
  #  return [{"start":5,"end":20,"headOrg":"org1","tailOrg":"org1"},
  #            {"start":1,"end":16,"headOrg":"org2","tailOrg":"org1"}]
  #
  #    start: start UTC time of the contact
  #    end: end UTC time of the contact
  #    headOrg is other user's organization during the contact
  #    tailOrg is the user(uid)'s organization during the contact
  #
  #  This endpoint takes the UID provided and queries the Neo4J 
  #  database to find all socialContact relationships with a matching 
  #  UID and returns an array with the attributes of each relationship.
  #
  #---------------------------------------------------------------
  def getSocialContacts(self, uid):
    endpt = "/getSocialContacts"
    req = {
      "uid": uid
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  addMembership(self, uid, org, role, accepted=False)      
  #    uid - userid
  #    org - org
  #    role - 'm' (member), 'a' (admin), or 'o' (owner)
  #
  #  return "Success" 
  #
  #  This endpoint creates a row in the Membership table using the 
  #  values provided. The accepted attribute shows if the membership 
  #  has been accepted by the organization and should be a value of 
  #  either 0 for false or 1 for true. As a guideline for how to use 
  #  the endpoint: when a user requests to join an organization the 
  #  accepted value should be set to 0 as opposed to when an admin 
  #  adds a member to the organization the accepted value should be 
  #  set to 1 since the organization has already accepted them. 
  #
  #---------------------------------------------------------------
  def addMembership(self, uid, org, role='m', accepted=False):      
    endpt = "/addMembership"
    req = {
      "uid": uid,
      "org": org,
      "role": role,
      "accepted": accepted if 1 else 0
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  inviteMember(self, org, email, role='m')
  #    org - organization to invite member to
  #    email - email of the user to send the invite
  #    role  - m/a/o role of the member in the organization
  #
  #  return "Success" or "Invalid Email" 
  #
  #  This endpoint is used to invite a user to join an organization. 
  #  An owner/admin can enter the email of a user to invite. The server 
  #  will then send an email invitation to the user who can click the 
  #  provided link to accept the invitation. If the provided email 
  #  does not exist, the server will return “Invalid email” but will 
  #  send an email to the user inviting them to join ViroGuard.
  #
  #---------------------------------------------------------------
  def inviteMember(self, org, email, role='m'):
    endpt = "/inviteMember"
    req = {
      "org": org,
      "targetEmail": email,
      "role": role,
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  acceptMembership(self, membershipId)
  #    membershipId - membership ID used to lookup membership 
  #
  #  return "Success" 
  #
  #  This endpoint is used when an administrator accepts a user’s 
  #  request to join an organization. It changes the ‘accepted’ 
  #  attribute of that user’s membership to 1 to signify that the 
  #  member has been accepted.
  #
  #---------------------------------------------------------------
  def acceptMembership(self, membershipId):
    endpt = "/acceptMembership"
    req = {
      "membershipID": membershipId
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res

      
  #---------------------------------------------------------------
  #
  #  delMembership(self, uid, org)
  #    uid - userid
  #    org - organization
  # 
  #    return "Success"
  #
  #  This endpoint deletes a row in the Membership table with 
  #  matching attributes to those provided. Additionally to being 
  #  used when removing a member from the organization, this 
  #  endpoint should be used when an administrator declines a 
  #  request to join an organization.
  #
  #---------------------------------------------------------------
  def delMembership(self, uid, org):
    endpt = "/deleteMembership"
    req = {
      "uid": uid,
      "org": org 
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res

      
  #---------------------------------------------------------------
  #
  #  infectionReport(self, uid, org, type, date, description, attachment)
  #    uid - userid
  #    org - organization
  #    type - report type (0-3)  
  #            0 - Symptomatic 
  #            1 - Exposed 
  #            2 - Tested positive 
  #            3 - Vaccinated 
  #    date - UTC date
  #    description - string of description text
  #    attachment - base64 string of S3 link where attachment is uploaded
  #
  #  return "Success"
  #
  #  This endpoint adds a row to the Reports table with the information 
  #  provided. If the report type is a vaccination report, the user’s 
  #  vaccinated attribute is updated as well to show that they have been 
  #  vaccinated. The attachment and description attributes are both 
  #  optional for the request and can be set to null if not provided 
  #  by the user.
  # 
  #---------------------------------------------------------------
  def infectionReport(self, uid, org, type, date, description, attachment):
    endpt = "/infectionReport"
    req = {
      "uid": uid,
      "org": org,
      "type": type,
      "date": date,
      "description": description,
      "attachment": attachment 
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  contactTrace(self, uid) 
  #    uid - userid
  #
  #  return "Success"     
  #
  #  This endpoint takes each socialContact relationship stemming 
  #  from the node with the matching UID and messages the user 
  #  attached to each relationship a warning that they may be affected.
  #
  #---------------------------------------------------------------
  def contactTrace(self, uid):      
    endpt = "/contactTrace"
    req = {
      "uid": uid
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  getOrganizations(self)
  #
  #  return [{"orgID":1,"name":"Test Organization","members":null,
  #           "orgLogo":null,"secretKey":null}]
  #
  #  This endpoint returns a list of all the organizations in the 
  #  format of an array of dictionaries that each store the 
  #  information of an organization.
  #
  #---------------------------------------------------------------
  def getOrganizations(self):
    endpt = "/getOrganizations"
    req = {
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  createOrganization(self, name)
  #    name - organiation name
  #    ... - ?  what are the other attributes?
  #
  #  return orgId           
  #
  #  This endpoint is used to create an organization. The request 
  #  only requires a name to be given, however additional information 
  #  about the organization can be sent as well. The complete process 
  #  of a user creating an organization additionally includes calling 
  #  the /addMembership endpoint to add the user who created the 
  #  organization as the owner using the ID of the organization that 
  #  is returned. 
  #
  #---------------------------------------------------------------
  def createOrganization(self, name):
    endpt = "/createOrganization"
    req = {
      "name": name
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  editOrgInfo(self, orgId, attribute, value)    
  #    orgId: organization ID to change
  #    attribute: attribute to change 
  #    value: new value for the attribute
  #
  #    return "Success"
  #
  #  This endpoint takes an attribute to edit and updates the column 
  #  with the matching attribute name on the row with the matching 
  #  orgID to the new value provided.
  #
  #---------------------------------------------------------------
  def editOrgInfo(self, orgId, attribute, value):
    endpt = "/editOrgInfo"
    req = {
      "org": orgId, 
      "attribute": attribute, 
      "value": value 
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res


  #---------------------------------------------------------------
  #
  #  getMembers(self, orgId)
  #    orgId - organization ID
  #
  #    return [
  #            {"membershipID":<ID>,"orgID":<Org>,"member":<UID>,
  #             "role":<Role>, “accepted”:<(0/1)>},
  #            {"membershipID":<ID>,"orgID":<Org>,"member":<UID>,
  #             "role":<Role>, “accepted”:<(0/1)>}
  #           ]
  #
  #  This endpoint queries the Membership list to find all rows with 
  #  a matching OrgID as the one provided and returns it. Each of 
  #  these memberships represent a member who is part of the organization. 
  #  The accepted value shows whether the member has been accepted by an 
  #  admin and is 0 for false and 1 for true. Those with an accepted 
  #  value of 0 are members who have requested to join but have not been 
  #  accepted yet.
  #
  #---------------------------------------------------------------
  def getMembers(self, orgId): 
    endpt = "/getMembers"
    req = {
      "org": orgId, 
    }
    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res

  
  #---------------------------------------------------------------
  #
  #  getMetrics(self, orgId)
  #    orgId: organization ID
  #
  #  returns: {"numReports":2, “numInfections”:1, "numViolations":1}
  #
  #  This endpoint takes an organization and queries the MySQL 
  #  database and counts the number of reports with a matching OrgID 
  #  to find the numReports. numInfections is gotten by queries the 
  #  MySQL database and counts the number of reports with a matching 
  #  OrgID and with a type value of 2. To get numViolations, the server 
  #  queries Neo4J and gets the number of socialContact relationships 
  #  where one of the users was in the organization during the time of 
  #  the violation.
  #
  #---------------------------------------------------------------
  def getMetrics(self, orgId, startDate=None, endDate=None):
    endpt = "/getMetrics"

    if (startDate is not None) and (endDate is not None):
      req = {
        "org": orgId, 
        "startDate": startDate,
        "endDate": endDate
      }
    else: 
      req = {
        "org": orgId, 
      }

    res = requests.post( self.baseURL + endpt, data=json.dumps(req), 
                       verify=self.certificate)
    return res



#===============================================================
#  Unit Test Class
#===============================================================
class UnitTest(unittest.TestCase):
  
  api = ViroGuardApi(
           url="https://backend.e-motion.ai", 
           cert="/home/pi/Software/PiBeaconTracker/ssl/emotion.ai.crt")
  

  #---------------------------------------------------------------
  #  Run the test cases
  #---------------------------------------------------------------
  def run(self): 

    #-------------
    print("Testing /getOrganizations")
    res = self.api.getOrganizations()
    orgs = json.loads(res.text)
    orgId = -1
    if len(orgs) > 0:
      orgId = orgs[0]["orgID"]
    self.assertEqual(res.status_code==200 and orgId != -1, True)
    print("Passed /getOrganizations")
      
    #-------------
    print("Testing /registerUser")
    uid = random.randint(0, 10000000)
    res =  self.api.registerUser(
      uid = uid, 
      name = "Flash Gordon", 
      orgs = [orgId], 
      phone = "+11234567890", 
      email = "emotionrobots@gmail.com"
    )
    uid2= random.randint(0, 10000000)
    res2=  self.api.registerUser(
      uid = uid2,
      name = "Flash Light Gordon",
      orgs = [orgId],
      phone = "+11234567891",
      email = "larrylisky@gmail.com"
    )
    self.assertEqual(res.status_code==200 and 
                     res.text=="Success" and
                     res2.status_code==200 and
                     res2.text=="Success" , True)
    print("Passed /registerUser")

    #-------------
    print("Testing /getUserInfo")
    res = self.api.getUserInfo(uid)
    r = json.loads(res.text)
    self.assertEqual( 
      (r["name"] == "Flash Gordon" and res.status_code==200),
      True
    )
    print("Passed /getUserInfo")
    
    #-------------
    print("Testing /editUserInfo")
    res1 = self.api.editUserInfo(uid, [{"attribute":"email", "value":"good@email.com"}])
    res2 = self.api.getUserInfo(uid)
    r = json.loads(res2.text)
    self.assertEqual(res1.status_code==200 and 
                     res2.status_code==200 and
                     res1.text=="Success" and
                     r["email"]=="good@email.com", True)
    print("Passed /editUserInfo")
     
    #-------------
    print("Testing /addCohabitant")
    res = self.api.addCohabitant(uid, "larrylisky@gmail.com")
    print(f"res.status_code={res.status_code}, res.text={res.text}")
    self.assertEqual(res.status_code==200, True)
    print("Passed /addCohabitant")


    #-------------
    print("Testing /xxx")
    res2 = self.api.getUserInfo(uid)
    print(f"res2.status_code={res2.status_code}, res2.text={res2.text}")
    '''
    r = json.loads(res2.text)
    self.assertEqual(res1.status_code==200 and
                     res2.status_code==200 and
                     res1.text=="Success" and
                     r["cohabitants"][0]==
    '''


#===============================================================
#
#  Main()
#
#===============================================================
def main(argv):
  testCases = UnitTest() 
  testCases.run()


if __name__ == '__main__':    
  main(sys.argv[1:])

