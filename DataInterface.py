__author__ = 'Jake'

#Imports functions to parse and modify XML database.

import xml.etree.ElementTree as ET
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import SubElement, ElementTree

# TODO: write function that finds student and returns the current absences


class DataInterface:
    """ This class contains all basic database management functions for Student CMS. When working with this class, it is
    important to maintain the integrity of the student data categories and the headerList instance variable to prevent
    errors in which one attempts to modify the attributes of a category which does not exist. """

    def __init__(self, fileloc="", year="", semester=""):
        """ Creates the database. If a file location (fileloc), the function open up a previously saved database.
        If no file location is passed, the function will use newDB to create a new database. """
        
        self.headerList = []        # creates the list of non-default data categories.
        if fileloc:
            tree = ET.parse(fileloc)  # reads from the database file into an ElementTree object
            self.data = tree.getroot()  # sets the root of this object to the global variable data.
            self.findHeaders() # loads all non-default data categories.
        else:
            self.data = self.newDB(year, semester)  # sets the global variable data to the root returned by newDB.

    
    def save(self, filename="database.xml"):
        """ Writes the database to the current folder. If a file name is passed, it will be saved under that name.
        If no name is passed, it will be saved under the default name "database.xml". """
        
        file = ElementTree(self.data)  # wraps the global variable data (an Element) in an ElementTree instance.
        file.write(filename)

    
    def newDB(self, year="", semester=""):
        """ Returns the root of a new ElementTree named "Gradebook" with the three subelements "Students", "Groups",
        and "Dates" for the three categories of data that could be stored in the database. Also stores the year
        and semester attributes for the Gradebook if those are passed. """
        
        root = ET.Element("Gradebook")  # creates the Gradebook element and adds its attributes.
        root.attrib["year"] = year
        root.attrib["semester"] = semester

        SubElement(root, "Students")  # adds the three SubElements of the Gradebook.
        SubElement(root, "Groups")
        SubElement(root, "Dates")

        return root  # returns the root to be saved as self.data.


    def findHeaders(self):
        """ findHeaders:  Deduces the list of non-default category headers by finding a non-flagged, non-dropped student
        and adding all of their non-default categories to the header list. NOT FOR EXTERNAL USE. """
        
        # creates the list of default categories and the empty header list.
        deflist = ["ID", "Units", "Number of Absences", "Number of Excused", "In Class", "Flag"]
        headerlist = []

        # finds the first non-flagged, non-dropped student and sets the list of their children to catlist.
        stulist = self.data.find("Students").getchildren()
        x = 0
        while(stulist[x].find("Flag").attrib["info"] == "Yes" or stulist[x].find("In Class").attrib["info"] == "No"):
            x += 1
        catlist = stulist[x].getchildren()

        # adds all categories whose tags are not a member of stdlist to headerlist.
        for x in range(0, len(headerlist)):
            if(catlist[x].tag not in deflist): headerlist.append(catlist[x].tag)

        # sets local headerlist equal to the instanced headerList.
        self.headerList = headerlist

    
    def addStudent(self, name):
        """ Creates a new student, with defaults of enrolled and unflagged.
        Student has all current column categories but without any values. """
        
        students = self.data.find("Students")  # finds the Students data category.
        student = SubElement(students, "Name") # adds a new subelement with the student's name as a tag.
        student.attrib["info"] = name
        # adds all default student data categories.
        SubElement(student, "ID")
        SubElement(student, "Units")
        SubElement(student, "Number of Absences")
        SubElement(student, "Number of Excused")
        SubElement(student, "In Class").attrib["info"] = "Yes"
        SubElement(student, "Flag").attrib["info"] = "No"

        # adds all additional data categories.
        for x in range(0, len(self.headerList)):
            SubElement(student, self.headerList[x])

    
    def findStudent(self, name):
        """ Returns the student Element with the tag of the given name. NOT FOR EXTERNAL USE. """
        
        students = self.data.find("Students")
        return students.find(name)

    
    def stuSort(self, vlist):
        """ Takes a list of student elements, removes all dropped or flagged students and sorts alphabetically.
        NOT FOR EXTERNAL USE. """
        
        nlist = []
        v2list = []

        for x in range(0, len(vlist)):
            if(vlist[x].find("Flag").attrib["info"] == "No" or vlist[x].find("In Class").attrib["info"] == "Yes"):
                   nlist.append(vlist[x].tag)
        nlist.sort()

        for x in range(0, len(nlist)):
            v2list.append(self.findStudent(nlist))

        return v2list

     
    def dropStudent(self, name):
        """ Sets the InClass attribute to indicate that the student has dropped. """
        
        student = self.findStudent(name)
        student.find("In Class").attrib["info"] = "No"

    
    def stuMod(self, name, header, value):
        """ Changes the attribute of the given header category within the given student element. """
        
        student = self.findStudent(name)
        student.find(header).attrib["info"] = value

    def stuCall(self, name, header):
        """ Modifies the attribute of the given header category within the given student element. """
        
        student = self.findStudent(name)
        return student.find(header).attrib["info"]

    
    def stuAdd(self, header, value=""):
        """ Adds a category with the tag given by the header to all students and adds this category to the list of
        categories which will be given to students added in the future. If a default is given in the value input
        this will be given to all students. This function will add duplicate categories, which will cause errors.
        Thus, this function should be used in conjunction with stuQuery which checks for duplicates. """
        
        self.headerList.append(header)
        students = self.data.find("Students")
        clist = students.getchildren()

        for x in range(0, len(clist)):
            if (value != ""):
                SubElement(clist[x], header).attrib["info"] = value
            else:
                SubElement(clist[x], header)

     
    def stuQuery(self, header):
        """ Returns true if the students have a category with the given header as a tag and false if they do not. Use
        this to avoid adding duplicate categories. """
        
        return header in self.headerList

     
    def stuMassMod(self, header, vlist):
        """ Changes all values of the given header to the corresponding values of a list of values. This list must
        include all non-flagged, non-dropped students and must be arranged in alphabetical order by student
        name. If the list given is the wrong size or the header is not a category, the function will return
        false. Otherwise, true will be returned. """
        
        slist = self.data.find("Students").getchildren()
        slist = self.stuSort(slist)

        if((len(slist) != len(vlist)) or (header in self.headerList)): return False

        for x in range(0, len(slist)):
            slist[x].find(header).attrib["info"] = vlist[x]

        return True

    
    def stuMassCall(self, header):
        """ Returns a list of the values each student has of a given category with the header as a tag. This
        list is in alphabetical order and only includes non-dropped, non-flagged students. If the given
        header is not the tag of a category, then the function will return None. """
        
        slist = self.data.find("Students").getchildren()
        slist = self.stuSort(slist)
        vlist = []

        if(header not in self.headerList): return ""

        for x in range(0, len(slist)):
            vlist.append(slist[x].find(header).attrib["info"])

        return vlist

    
    def stuRec(self, name):
        """ Reconciles a student's categories with the database headerList. Should be used whenever a student
        is un-flagged or un-dropped. """
        
        student = self.findStudent(name)
        catlist = student.getchildren()
        stdlist = ["ID", "Units", "Number of Absences", "Number of Excused", "In Class", "Flag"]

        if(len(catlist) == (len(self.headerList)+6)): return True

        localheaders = []
        for x in range(0, len(catlist)):
            if(catlist[x].tag not in stdlist): localheaders.append(catlist[x].tag)

        for x in range(0, len(self.headerList)):
            if(self.headerList[x] not in localheaders): SubElement(student, self.headerList[x])

    
    def stuCatMod(self, target, name):
        """ Allows the tag of a preexisting student category to be changed without effecting the category's
        stored data. """
        
        if(target not in self.headerList): return False
        self.headerList.remove(target)

        stulist = self.data.find("Students").getchildren()
        for x in range(0, len(stulist)):
            if(stulist[x].find(target)): stulist[x].find(target).tag = name
            else: SubElement(stulist[x], name)

        return True

















