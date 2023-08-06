#!/usr/bin/python
# -*- coding: utf-8 -*-


# Daaayonearth - Copyright & Contact Notice
#############################################
#  Created by Dominik Niedenzu              #      
#  Copyright (C) 2021-2022 Dominik Niedenzu #       
#      All Rights Reserved                  #
#                                           #
#            Contact:                       #
#       blythooon@blackward.de              #         
#       www.blackward.de                    #         
#############################################

# Daaayonearth - Version & Modification Notice
##############################################
# Based on Daaayonearth Version 0.75         #
# Modified by --- (date: ---)                #
##############################################

# Daaayonearth - License
#######################################################################################################################
# Use and redistribution of this software in source and binary forms, without or with modification,                   #
# are permitted (free of charge) provided that the following conditions are met (including the disclaimer):           #
#                                                                                                                     #
# 1. Redistributions of source code must retain the above copyright & contact notice and                              #
#    this license text (including the permission notice, this list of conditions and the following disclaimer).       #
#                                                                                                                     #
#    a) If said source code is redistributed unmodified, the belonging file name must be daaayonearth.py and          #
#       said file must retain the above version & modification notice too.                                            #
#                                                                                                                     #
#    b) Whereas if said source code is redistributed modified (this includes redistributions of                       #
#       substantial portions of the source code), the belonging file name(s) must be daaayonearth_modified*.py        #
#       (where the asterisk stands for an arbitrary intermediate string) and said files                               #
#       must contain the above version & modification notice too - updated with the name(s) of the change             #
#       maker(s) as well as the date(s) of the modification(s).                                                       #
#                                                                                                                     #
# 2. Redistributions in binary form must reproduce the above copyright & contact notice and                           #
#    this license text (including the permission notice, this list of conditions and the following disclaimer).       #
#    They must also reproduce a version & modification notice similar to the one above - in the                       #
#    sense of 1. a) resp. b).                                                                                         #
#                                                                                                                     #
# 3. Neither the name "Dominik Niedenzu", nor the name resp. trademark "Blackward", nor the names of authors resp.    #
#    contributors resp. change makers may be used to endorse or promote products derived from this software without   #
#    specific prior written permission.                                                                               #
#                                                                                                                     #
# 4. This software is able to request and download third party data from the internet resp. from third party web      #
#    services / pages. Said third party data as well as the belonging third party web services / pages come           #
#    with their own (different) licenses / terms and conditions. The user resp. redistributor of this software        #
#    (or parts of this software) must also take into account, respect and comply with all third party licenses /      #
#    terms and conditions.                                                                                            #
#    Using (including modifying) or/and redistributing this software in a way that leads to the infringement          #
#    (whether immediately or indirectly) of one or several third party licenses or other third party rights will      #
#    automatically terminate the user's resp. redistributor's rights under this license.                              #
#                                                                                                                     #
# 5. By using (including modifying) this software, the user confirms that he has also taken note of all further       #
#    license hints and that he complies with them. By using (including modifying) this software, the user also        #
#    confirms that he has taken note of all terms and conditions of web services / pages from which this software     #
#    might request / download data - in particular: https://www.openstreetmap.org, https://nominatim.org/ and         #
#    https://ec.europa.eu/jrc/en/pvgis - and that he complies with them.                                              #
#                                                                                                                     #
# THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO   #
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.                            #
#                                                                                                                     #
# IN NO EVENT SHALL DOMINIK NIEDENZU OR AUTHORS OR CONTRIBUTORS OR CHANGE MAKERS BE LIABLE FOR ANY CLAIM, ANY         #
# (DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY OR CONSEQUENTIAL) DAMAGE OR ANY OTHER LIABILITY, WHETHER IN AN    #
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THIS SOFTWARE (OR PARTS OF THIS   #
# SOFTWARE) OR THE USE OR REDISTRIBUTION OR OTHER DEALINGS IN THIS SOFTWARE (OR PARTS OF THIS SOFTWARE).              #
#                                                                                                                     #
# THE USERS RESP. REDISTRIBUTORS OF THIS SOFTWARE (OR PARTS OF THIS SOFTWARE) ARE SOLELY RESPONSIBLE FOR ENSURING     #
# THAT AFOREMENTIONED CONDITIONS ALL ARE MET AND COMPLIANT WITH THE LAW IN THE RESPECTIVE JURISDICTION - BEFORE (!)   #
# THEY USE RESP. REDISTRIBUTE.                                                                                        #
#######################################################################################################################

# Daaayonearth - Further License Hints
#######################################################################################################################
#                                                                                                                     #
# The 'Location' class uses the 'Nominatim' geocoding service / API of 'OpenStreetMap' ((C) OpenStreetMap             #
# contributors - data licensed under the 'ODbL' by the OpenStreetMap Foundation) - via the 'geopy' library.           #
#                                                                                                                     #
# Please note, that the Nominatim’s Usage Policy requires you to specify a valid HTTP Referer resp. User-Agent        #
# identifying the application (stock User-Agents as set by http libraries will not do). Have a look at the module's   #
# global variable 'userAgentNameS' used in the 'Location' class.                                                      #
#                                                                                                                     #
# Further informations about the belonging licenses resp. terms and conditions can be found on the following web      #
# pages:                                                                                                              #
#                                                                                                                     #
# https://geopy.readthedocs.io/en/stable/#nominatim                                                                   #
# https://nominatim.org/                                                                                              #
# https://operations.osmfoundation.org/policies/nominatim/                                                            #
# https://opendatacommons.org/licenses/odbl/1-0/                                                                      #
# https://www.openstreetmap.org/about                                                                                 #
# https://www.openstreetmap.org/copyright                                                                             #
#                                                                                                                     #
#                                                                                                                     #
# The 'EnvConditions' class uses the non-interactive service / API of 'PVGIS' ((C) European Communities, 2001-2021)   #
# of the 'EU SCIENCE HUB' for acquiring geographical, meteorological and photovoltaic informations.                   #
#                                                                                                                     #
# Please feel free to also have a look at the publication of Huld, T., Müller, R. and Gambardella, A., 2012:          #
# 'A new solar radiation database for estimating PV performance in Europe and Africa'. Solar Energy, 86, 1803-1815.   #
#                                                                                                                     #
# Further informations about the belonging licenses resp. terms and conditions can be found on the following web      #
# pages:                                                                                                              #
#                                                                                                                     #
# https://ec.europa.eu/jrc/en/pvgis                                                                                   #
# https://ec.europa.eu/jrc/en/PVGIS/docs/noninteractive                                                               #
# https://ec.europa.eu/info/legal-notice_en                                                                           #
# https://creativecommons.org/licenses/by/4.0/                                                                        #
#                                                                                                                     #
#                                                                                                                     #
# This 'Further License Hints' section is just meant as a convenience to support giving you an entry point into the   #
# topic of licenses, terms and conditions and so on. Said section (and its contents) is NOT intended to have legal    #
# significance - one cannot rely on resp. refer to it.                                                                #
#                                                                                                                     #
# It just reflects the knowledge of the author at the time of this writing - it or/and its contents may be            #
# incomplete, incorrect or/and outdated!                                                                              #
#                                                                                                                     #
# Accordingling, reading said section is not an equal replacement for reading all licenses, terms and                 #
# conditions, notes and texts belonging to the data, APIs, services or/and web pages used.                            #
#                                                                                                                     #
#######################################################################################################################



############################################################
#                                                          #
# The API of this module (just) consists of three classes: #
#                                                          #
# 'Location', 'TimeZone' and 'EnvConditions'               #
#                                                          #
# and a global variable:                                   #
#                                                          #
# 'UserAgentNameS'                                         #
#                                                          #
# (which initially has to be set to the application's      #
#  name)                                                   #
#                                                          #
# - for a description see the belonging doc-texts.         #
#                                                          #
############################################################



#import from common libraries
from   geopy.geocoders   import Nominatim       as OpenStreetMap_Geocoder
from   timezonefinder    import TimezoneFinder
from   datetime          import tzinfo          as Tzinfo
from   dateutil          import tz              as Dateutil_tz
from   datetime          import date            as Date
from   datetime          import time            as Time
from   datetime          import datetime        as Datetime
from   datetime          import timezone        as Datetime_timezone
from   urllib.request    import urlopen         as Urlopen
from   io                import BytesIO
from   re                import search          as Re_search
from   re                import compile         as Re_compile
from   pandas            import read_csv        as Pd_read_csv
from   pandas            import DataFrame
from   scipy.interpolate import interp1d        as Scipy_interp1d
from   matplotlib.figure import Figure
from   numpy             import linspace        as Numpy_linspace
from   numpy             import array           as Array
from   warnings          import simplefilter    as Warnings_simplefilter


#some preparations
UserAgentNameS = None                                            #set this to the name of the application using the 'Location' class
Warnings_simplefilter(action='ignore', category=FutureWarning)   #suppress future warnings
__version__    = 0.75



#(latitude, longitude) named tuple
class Location(tuple):
      """ 
           Note that, before you can use the geocoding functionality of this class, you have to set the global 
           variable (of this module 'daaayonearth') 'UserAgentNameS' to a string containing the name of the application
           using this class (resp. said functionality) - to comply with the Nominatim’s Usage Policy! Note, that said
           application name is/might be transmitted!

           Examples:
           =========
           
           location = Location( "Berlin, Brandenburger Tor"                          )
           location = Location( (52.51628045,                   13.377701882994323)  )
           location = Location( 52.51628045,                    13.377701882994323   )
           location = Location( 52.51628045,          longitude=13.377701882994323   )
           location = Location( latitude=52.51628045, longitude=13.377701882994323   )
           
           all leads to the very same - a sort of a 'named tuple' with:
           
           location           == (52.51628045, 13.377701882994323)
           location.latitude  == 52.51628045
           location.longitude == 13.377701882994323
      """       

      latitude       = None
      longitude      = None

        
      #creator
      def __new__(self, latitude, longitude=None):
          """ 
               Note that the 'latitude' parameter might contain a latitude float, 
               an address string or a (latitude, longitude) tuple!
               
               (So, the keyword name 'latitude' sometimes is somehow 'abused' here -
               for code simplicity...)
          """

          global UserAgentNameS
        
          #get types of parameters and check whether combination is valid
          paramTypesT = (type(latitude), type(longitude))
          if paramTypesT not in ((str, type(None)), (tuple, type(None)), (Location, type(None)), (float, float)):
             raise Exception("Error in Location.__new__: invalid set of parameters (%s, %s)!" % (latitude, longitude))
            
          #handle parameters
          if    longitude == None:
                #single parameter (string or tuple) has been given
                if    isinstance(latitude, str):
                      #just an ADDRESS STRING has been given

                      #ensure, that the UserAgentNameS has been set
                      if (not isinstance(UserAgentNameS, str)) or (len(UserAgentNameS) <= 0):
                         raise Exception( "Error in Location.__new__: the geocoding functionality just can be used after the global "       \
                                          "variable 'UserAgentNameS' (of module daaayonearth) has been set to the name of the application " \
                                          "(string) which uses this class -- in accordance with the Nominatim’s Usage Policy!"              )
                    
                      #get belonging geo location - if any
                      geolocator           = OpenStreetMap_Geocoder(user_agent=UserAgentNameS)
                      try:
                             locationT     = geolocator.geocode(latitude)
                             if locationT == None:
                                raise Exception("Geolocating failed...")
                                
                             locationT     = (locationT.latitude, locationT.longitude)
                    
                      except BaseException:
                             raise Exception("Error in Location.__new__: resolving the geo location belonging to '%s' failed!" % latitude)
                    
                elif  isinstance(latitude, tuple):
                      #just a GEOLOCATION (latitude, longitude) TUPLE has been given
                    
                      #check latitude
                      if not (isinstance(latitude[0], float) and (-90.0 <= latitude[0] <= 90.0)):
                         raise Exception("Error in Location.__new__: latitude must be a float with -90.0 <= latitude <= 90.0 (%s)!" % latitude[0])
                    
                      #check longitude
                      if not (isinstance(latitude[1], float) and (-180.0 <= latitude[1] <= 180.0)):
                         raise Exception("Error in Location.__new__: longitude must be a float with -180.0 <= longitude <= 180.0 (%s)!" % latitude[1])
                    
                      locationT = latitude
                
                else:
                      #should never happen
                      raise Exception("Error in Location.__new__: unexpected error!")
                    
          else:
                #check latitude
                if not (-90.0 <= latitude <= 90.0):
                   raise Exception("Error in Location.__new__: latitude must be a float with -90.0 <= latitude <= 90.0 (%s)!" % latitude)
                
                #check longitude
                if not (-180.0 <= longitude <= 180.0):
                   raise Exception("Error in Location.__new__: longitude must be a float with -180.0 <= longitude <= 180.0 (%s)!" % longitude)  
                
                locationT = (latitude, longitude)
                
          #create a kind of a named tuple
          retT = tuple.__new__(self, locationT)
          retT.latitude  = locationT[0]
          retT.longitude = locationT[1]
            
          #return
          return retT
        
        
      #constructor
      def __init__(self, *paramL, **paramD):
          """ Just to prevent the calling of the constructor of the parent class. """
        
          pass
        
        
      #selftest
      @classmethod
      def _selftest(cls):
          """ If this method does not lead to an exception, the class works as expected. """
        
          print ("Testing 'Location' class...")
            
          #single address string
          location = Location("Berlin, Brandenburger Tor")
          assert location == (52.51628045, 13.377701882994323) == (location.latitude, location.longitude)
            
          #single geo location tuple
          location = Location( (11.23, 22.34) )
          assert location == (11.23, 22.34) == (location.latitude, location.longitude)            
            
          #two positional floats
          location = Location(11.23, 22.34)
          assert location == (11.23, 22.34) == (location.latitude, location.longitude)            
            
          #two keywaord floats
          location = Location(latitude=11.23, longitude=22.34)
          assert location == (11.23, 22.34) == (location.latitude, location.longitude)
        
          #one positional and one keyword float
          location = Location(11.23, longitude=22.34)
          assert location == (11.23, 22.34) == (location.latitude, location.longitude) 
            
          #verify doc text example
          assert Location( "Berlin, Brandenburger Tor" )                        == Location( (52.51628045, 13.377701882994323)                  ) == \
                 Location( 52.51628045, 13.377701882994323 )                    == Location( 52.51628045, longitude=13.377701882994323          ) == \
                 Location( latitude=52.51628045, longitude=13.377701882994323 ) == (52.51628045, 13.377701882994323)
          assert Location( "Berlin, Brandenburger Tor" ).latitude               == 52.51628045
          assert Location( "Berlin, Brandenburger Tor" ).longitude              == 13.377701882994323
            
          print ("...'Location' class successfully tested!")



#timezone, subclass of Tzinfo
class TimeZone(Tzinfo):
      """
           Examples:
           =========
           
           timezone = TimeZone( Location("Berlin, Brandenburger Tor")                )
           timezone = TimeZone( "Berlin, Brandenburger Tor"                          )
           timezone = TimeZone( (52.51628045,                   13.377701882994323)  )
           timezone = TimeZone( 52.51628045,                    13.377701882994323   )
           timezone = TimeZone( 52.51628045,          longitude=13.377701882994323   )
           timezone = TimeZone( latitude=52.51628045, longitude=13.377701882994323   )
           
           all leads to the very same - a 'Tzinfo' object usable alike the following:
           
           summerBerlin = datetime.datetime(2021, 10, 31, tzinfo=timezone)     
           winterBerlin = datetime.datetime(2021, 11,  1, tzinfo=timezone) 
           
           ==>
           
           str(summerBerlin) == "2021-10-31 00:00:00+02:00"
           str(winterBerlin) == "2021-11-01 00:00:00+01:00"
      """
        
      #creator
      def __new__(self, latitude, longitude=None):
          """ 
               Note that the 'latitude' parameter might contain a latitude float, 
               an address string or a (latitude, longitude) tuple!
               
               (So, the keyword name 'latitude' sometimes is somehow 'abused' here -
               for code simplicity...)
          """
        
          #get (latitude, longitude) location 'named' tuple belonging to parameters (latitude, longitude)
          try:
                 location = Location( latitude, longitude )
                
          except BaseException as ee:
                 raise Exception( "Error in TimeZone.__new__: creating a 'Location' object belonging " \
                                  "to parameters (%s, %s) failed (%s)!" % (latitude, longitude, ee)    )
        
          #get the timezone string belonging to location
          try:
                 timezoneFinder = TimezoneFinder()
                 timezoneS      = timezoneFinder.timezone_at(lat=location.latitude, lng=location.longitude)
                    
          except BaseException as ee:
                 raise Exception( "Error in TimeZone.__new__: finding a timezone string belonging" \
                                  "to '%s' failed (%s)!" % (location, ee)                          )
            
          #create the timezone object (Tzinfo) belonging to the timezone string
          try:
                 tzinfo = Dateutil_tz.gettz(timezoneS)
                    
          except BaseException as ee:
                 raise Exception( "Error in TimeZone.__new__: creating a timezone object belonging " \
                                  "to '%s' failed (%s)!" % (timezoneS, ee)                           )       
        
          #return
          return tzinfo
        
        
      #constructor
      def __init__(self, *paramL, **paramD):
          """ Just to prevent the calling of the constructor of the parent class. """
        
          pass


      #selftest
      @classmethod
      def _selftest(cls):
          """ If this method does not lead to an exception, the class works as expected. """
        
          print ("Testing 'TimeZone' class...")
            
          assert TimeZone( Location("Berlin, Brandenburger Tor")                ) == \
                 TimeZone( "Berlin, Brandenburger Tor"                          ) == \
                 TimeZone( (52.51628045,                   13.377701882994323)  ) == \
                 TimeZone( 52.51628045,                    13.377701882994323   ) == \
                 TimeZone( 52.51628045,          longitude=13.377701882994323   ) == \
                 TimeZone( latitude=52.51628045, longitude=13.377701882994323   )
                 
          timezone     = TimeZone( latitude=52.51628045, longitude=13.377701882994323 )
                 
          summerBerlin = Datetime(2021, 10, 31, tzinfo=timezone)     
          winterBerlin = Datetime(2021, 11,  1, tzinfo=timezone) 
            
          assert str(summerBerlin) == "2021-10-31 00:00:00+02:00"
          assert str(winterBerlin) == "2021-11-01 00:00:00+01:00"
            
          print ("...'TimeZone' class successfully tested!")
          
          
          
#main class of this module (environmental conditions)
class EnvConditions(object):
      """
           An instance of EnvConditions contains the environment conditions belonging to a typical
           day at 'location' on 'date', whereby 'location' and 'date' are the parameters of its 
           constructor. The deviation between the given typical day data and the data belonging to a 
           real day (obviously) is not known - the number of provided decimal places accordingly
           does not have any (scientific) meaning. 

           Further details belonging to the parameters 'location' as well as 'date' can be found in the
           help/doc-text of the constructor (__init__).

           !!!TBD!!!: due to the chosen 'cubic' interpolation method values of a physical measurand, where
           negative values are not sensible, can become negative - yet.

           API:
           ====
           
           
           self.getDictOfFcts() ==> returns a dictionary of functions describing the environmental conditions belonging to
           
           self.location and self.dateTime
           
           - said functions each takes one parameter: the time on said day of the year in seconds (0..86400).


           self.getFigureOf("T") ==> returns a plot containing the course of temperature belonging to 

           self.location and self.dateTime

           - other options are:
           
           "Humidity"
           "Irradiance"
           "WindSpeed"
           "WindDirection"
           "Pressure"
           "PvPower"
           "SunHeight".
      """
      
      #parameters - selected by user
      location            = None
      timeZone            = None
      dateTime            = None
        
      #intermediate results (original data)
      _tmyDataFrame       = None                #typical meterological year data - belonging to selected day
      _pvpDataFrame       = None                #photovoltaic performance data - belonging to selected day
    
      #results (hourly medianed data)
      tmyDataFrame        = None                #typical meterological year data - belonging to selected day
      pvpDataFrame        = None                #photovoltaic performance data - belonging to selected day    
      functionsD          = None                #THE RESULT!!!
        
      ### columns to be renamed and how ###
      _colRenamesD        = dict() 
        
      #typical meterological year data
      _colRenamesD["TMY"] = {                                         \
                              "time(UTC)" : "DayTime [s]",            \
                              "T2m"       : "T(2m) [°C]",             \
                              "RH"        : "Humidity [%]",           \
                              "G(h)"      : "Irradiance [W/m^2]",     \
                              "WS10m"     : "WindSpeed(10m) [m/s]",   \
                              "WD10m"     : "WindDirection(10m) [°]", \
                              "SP"        : "Pressure(0m) [Pa]"       \
                            } #note: 'Gb(n)', 'Gd(h)', 'IR(h)' are deleted (as they are not of interest); 
                              #Irradiance: total sun irradiance on a horizontal plane
                              #WindDirection: 0 = N, 90 = E, ...
                
      #photovoltaic performance data
      _colRenamesD["PVP"] = {                                         \
                              "time"      : "DayTime [s]",            \
                              "P"         : "PvPower [W]",            \
                              "H_sun"     : "SunHeight [°]"           \
                            } #note: a system with peak power 1kW, no loss and a two axis autotracking is assumed 
                              #(so to say an ideal system limited to 1kW)
        
      ### columns to be deleted ###
      _delColsD           = dict()
        
      #typical meterological year data
      _delColsD["TMY"]    = ("Gb(n)", "Gd(h)", "IR(h)")
        
      #photovoltaic performance data
      _delColsD["PVP"]    = ("G(i)", "T2m", "WS10m", "Int")

      #regular expression for checking the parameter 'date' - if of type string
      _paramDateRe             = Re_compile(r"[0-1][0-9][-][0-3][0-9]")
        

      #constructor
      def __init__(self, location, date, auto=True):
          """
              Parameters:
              ===========
              
              location : of type 'Location' (or a 'str' valid as parameter of constructor of said 'Location' class)
              date     : of type 'datetime.date' (or a 'str' in the format 'mm-dd')
              auto     : 'True' if this constructor should automatically setup the complete environment conditions, 
                         'False' if one wants to do that 'manually' - for details have a look at the code
          """

          #allow parameter location to be a string too
          if    isinstance(location, str):
                #convert to Location type
                locationO = Location(location)

          else:
                locationO = location

          #allow parameter date to be a string too
          if    isinstance(date, str):
                if self._paramDateRe.match(date) == None:
                   raise Exception( "Error in EnvConditions.__init__: if parameter 'date' is of type string, it must have "    \
                                    "the format 'mm-dd', whereby 'mm' is a (zero padded) two digit number denoting the month " \
                                    "and 'dd' is a (zero padded) two digit number denoting the day -> 12-31 for example "      \
                                    "stands for the 31th of December (%s)!" % date                                             )

                #parameter date seems to be a str in the format mm-dd
                dateO = Datetime.strptime("2022-" + date, "%Y-%m-%d").date()

          else:
                dateO = date
        
          #ensure that the parameters are of correct types
          if (not isinstance(locationO, Location)) or (not isinstance(dateO, Date)):
             raise Exception( "Error in EnvConditions.__init__: parameter 'location' must be an instance of the 'Location' "   \
                              "class and parameter 'date' must be an instance of the 'datetime.date' class (%s, %s)!"        % \
                              (locationO, dateO)                                                                                 )
            
          #init attributes immediately derived from parameters
          self.location      = locationO
          self.timeZone      = TimeZone( locationO )
          self.dateTime      = Datetime.combine( dateO, Time(), tzinfo=self.timeZone )
            
          #create a dictionary of functions describing the course of day of TMY/PVP variables
          self.functionsD    = dict()
            
          #setup environment conditions
          if auto == True:
             self.loadTmy()
             self.processTmy()
             self.loadPvp()
             self.processPvp()
             self.cleanUp()
                
                
      #the only API method - use this!
      def getDictOfFcts(self):
          """ Get a dictionary of functions describing the course of the day of environmental parameters. """
        
          return self.functionsD
        
        
      #create a data frame with hourly median values
      def _getHourlyMedianDataFrame(self, origDataFrame):
          """ Internal helper method. """
        
          #create new, empty data frame
          dataFrame = DataFrame()
        
          #loop over 24 hours (in seconds)
          for indexI in range(24):
              #create a new row with median values belonging to time interval
              currRow  = self._getMedianOfInterval( origDataFrame, indexI * 3600, (indexI+1) * 3600 ).to_frame().transpose()
            
              #append row
              dataFrame = dataFrame.append( currRow )
           
          #return
          return dataFrame         
        
        
      #get median of time interval from beginF to endF-1 (seconds)
      def _getMedianOfInterval(self, dataFrame, beginF, endF):
          """ Internal helper method. """
        
          df = dataFrame.copy()
          df = df[ df["DayTime [s]"].apply( lambda el: True if (beginF <= el < endF) else False ) ]
        
          return df.median()
            
            
      #load data
      def _preProcessDataFrame(self, dataFrame, typeS="TMY"):
          """ Internal helper method. """
        
          #work on 'df'
          df = dataFrame.copy()
        
          #delete unnecessary columns
          for columnS in self._delColsD[typeS]:
              df.drop(columnS, axis=1, inplace=True)
        
          #rename columns
          df.rename(columns=self._colRenamesD[typeS], inplace=True)
        
          #convert time column to local time datetime instances
          df["DayTime [s]"] = df["DayTime [s]"].apply( self._utcStrToLocalDatetime )
        
          #delete data (rows) not belonging to (month,day) of self.dateTime
          df = df[ df["DayTime [s]"].apply( self._isTargetDay ) ]
        
          #convert time column to day time in seconds
          df["DayTime [s]"] = df["DayTime [s]"].apply( self._dateToDaytimeInSecs )        
        
          #return
          return df
    
                
      #convert date to seconds
      def _dateToDaytimeInSecs(self, date):
          """ Internal helper method. """
        
          return int( (date.replace(year=self.dateTime.year) - self.dateTime).seconds )
                                                                    
            
      #is date target day in year
      def _isTargetDay(self, date):
          """
              Returns True if month and day of 'date' is the very same as of 'self.dateTime'.
          """
        
          return ((date.month == self.dateTime.month) and (date.day == self.dateTime.day))
             
        
      #UTC str to local datetime
      def _utcStrToLocalDatetime(self, utcS):
          """
              Converts a UTC string to a datetime.datetime instance in local time given by self.timeZone.
          """
        
          return (Datetime.strptime( utcS, "%Y%m%d:%H%M" ).replace(tzinfo=Datetime_timezone.utc)).astimezone( self.timeZone )
          
            
      #download data from url and convert to pandas DataFrame
      def _downloadDataFrame(self, urlS, cropPatternStrT):
          """ Internal helper method. """
        
          #download/read webpage content
          try:
                 contentBytes = Urlopen(urlS).read()
        
          except BaseException as ee:
                 raise Exception("Error in EnvConditions._downloadDataFrame: downloading/reading from '%s' failed (%s)!" % (urlS, ee))
                    
          #crop header/footer
          try:
                 #convert start/stop crop pattern string to bytes
                 cropT        = (bytes(cropPatternStrT[0], "utf-8"), bytes(cropPatternStrT[1], "utf-8"))
                
                 #find start and end of table data (without header/footer)
                 startI       = Re_search( cropT[0], contentBytes ).start()
                 endI         = Re_search( cropT[1], contentBytes ).start()                
                
                 #crop content
                 contentBytes = contentBytes[startI:endI]
                    
          except BaseException as ee:
                 raise Exception("Error in EnvConditions._downloadDataFrame: cropping using '%s' failed (%s)!" % (cropPatternStrT, ee))  
                
          #convert to pandas DataFrame
          try:
                 #read table into a pandas DataFrame
                 dataFrame = Pd_read_csv( BytesIO(contentBytes) )
                    
          except BaseException as ee:
                 raise Exception("Error in EnvConditions._downloadDataFrame: converting to pandas DataFrame failed (%s, %s -> %s)!" % (urlS, cropPatternStrT, ee))
                
          #return data frame
          return dataFrame
      
        
      #create a figure containing a plot
      def _createFigure(self, fctKeyS, titleS):
          """ Internal helper method. """
          
          #create and configure figure
          figure = Figure( figsize=(16,9) )
          figure.set_facecolor("white")
          figure.suptitle(titleS)
          
          axes   = figure.add_subplot()
          
          #plot data
          xes    = Numpy_linspace(0, 24, 4*24 + 1)
          yes    = self.getDictOfFcts()[fctKeyS]( xes * 3600 )
          axes.plot(xes, yes)
          
          #configure axes
          axes.xaxis.set_ticks( range(25) )
          axes.set_xlabel( "Time[h]" )
          axes.set_ylabel( fctKeyS )
          axes.grid(True, color="lightgray", linestyle="--")

          #return
          return figure


      #get a plot belonging to nameS
      def getFigureOf(self, nameS):
          """ 
              nameS can be a string starting with one of the dfollowing strings:
              'T'
              'Humidity'
              'Irradiance'
              'WindSpeed'
              'WindDirection'
              'Pressure'
              'PvPower'
              'SunHeight'
          """

          #find key fitting to nameS
          for keyS in self.functionsD.keys():
              if keyS.startswith( nameS ):
                 break
             
          #define titles
          titleD = dict()
          titleD["T(2m) [°C]"]             = "Air temperature 2 meters above ground"
          titleD["Humidity [%]"]           = "Relative air humidity"
          titleD["Irradiance [W/m^2]"]     = "Total solar irradiance on a horizontal plane" 
          titleD["WindSpeed(10m) [m/s]"]   = "Wind speed 10 meters above ground"
          titleD["WindDirection(10m) [°]"] = "Wind direction (0° = N, 90° = E, 180° = S, 270° = W)"
          titleD["Pressure(0m) [Pa]"]      = "Air pressure on ground"
          titleD["PvPower [W]"]            = "Power of a (idealized) photovoltaic system \n " \
                                             "(crystalline silicon, peak power: 1kW, \n"      \
                                             "loss: 0%, 2-axis-autotracking)"
          titleD["SunHeight [°]"]          = "'Slope' angle of sun"
          
          #return
          months  = ("Jan.", "Feb.", "Mar.", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec.")
          titleS  = "-- Typical conditions on %d. %s at <lat: %.4f°, long: %.4f°> -- \n" %                            \
                    (self.dateTime.day, months[self.dateTime.month-1], self.location.latitude, self.location.longitude)
          titleS += titleD[keyS]
          return self._createFigure(keyS, titleS)


      #loads the data belonging to the typical meterological year
      def loadTmy(self):
          """ 
              Loads the data belonging to the typical meterological year.

              If you want to setup the environment conditions 'manually', this method has to be
              called before calling 'self.processTmy' ...
          """
          #load TMY (typical meterological year) data
          urlS               = "https://re.jrc.ec.europa.eu/api/tmy?lat=%f&lon=%f" % self.location
          dataFrame          = self._downloadDataFrame( urlS, ("time", "T2m:") )
    
          #preprocess data
          dataFrame          = self._preProcessDataFrame( dataFrame, "TMY" )      
    
          #store intermediate data frame
          self._tmyDataFrame = dataFrame


      #processes the data belonging to the typical meterological year
      def processTmy(self):
          """ 
              Processes the data belonging to the typical meterological year.

              If you want to setup the environment conditions 'manually', this method has to be
              called before you can access the data and/or the functions belonging to a 
              meterological day.
          """

          #create TMY day data
          self.tmyDataFrame = self._getHourlyMedianDataFrame( self._tmyDataFrame )
    
          #create and add TMY day functions
          for colS in self.tmyDataFrame.columns:
              self.functionsD[colS] = Scipy_interp1d( self.tmyDataFrame["DayTime [s]"].to_numpy(),                               \
                                                      self.tmyDataFrame[colS].to_numpy(), kind='cubic', fill_value="extrapolate" )                                                                                                               


      #loads the data belonging to the photovoltaic performance
      def loadPvp(self):
          """ 
              Loads the data belonging to the photovoltaic performance.

              If you want to setup the environment conditions 'manually', this method has to be
              called before calling 'self.processPvp'.
          """

          #load PVP (photovoltaic performance) data
          urlS               = "https://re.jrc.ec.europa.eu/api/seriescalc?lat=%f&lon=%f&pvcalculation=1&peakpower=1&loss=0&trackingtype=2" % self.location
          dataFrame          = self._downloadDataFrame( urlS, ("time", "P: PV") )
    
          #preprocess data
          dataFrame          = self._preProcessDataFrame( dataFrame, "PVP" )
    
          #store intermediate data frame
          self._pvpDataFrame = dataFrame


      #processes the data belonging to the photovoltaic performance
      def processPvp(self):
          """ 
              Processes the data belonging to the typical meterological year.

              If you want to setup the environment conditions 'manually', this method has to be
              called before you can access the data and/or the functions belonging to a 
              photovoltaic day.
          """

          #create PVP day data
          self.pvpDataFrame = self._getHourlyMedianDataFrame( self._pvpDataFrame )  
    
          #create and add PVP day functions
          for colS in self.pvpDataFrame.columns:
              self.functionsD[colS] = Scipy_interp1d( self.pvpDataFrame["DayTime [s]"].to_numpy(),                               \
                                                      self.pvpDataFrame[colS].to_numpy(), kind='cubic', fill_value="extrapolate" )
                    

      #delete temporary day time column 
      def cleanUp(self):
          """ 
              If you want to setup the environment conditions 'manually', this method has to be
              called at the end.
          """

          #day time is not an y-axis (but the x-axis)
          del self.functionsD["DayTime [s]"]


#selftest of module
def selftest():
    """ 
        If this method does not lead to an exception, the module works as expected. 
        !!!TBD!!!: selftest of EnvConditions still is missing.
    """
    
    Location._selftest()
    TimeZone._selftest()
    print ("Selftest of EnvConditions: to be done!")




if __name__ == "__main__":
   selftest()






