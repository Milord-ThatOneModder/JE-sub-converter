from xml.dom import minidom, getDOMImplementation
import base64
import gzip
import sys
import re
import os

def add_by_id(job, waypoints, displacement):
    # job = 'commanding_officer'
    # TODO check if waypoint wint end up in a fucking wall or worse, outside. For now its user problem :barodev:
    x = str(int(waypoints['x']) + displacement)
    y = waypoints['y']
    idcards = waypoints['idcardtags']
    if idcards.find("id_" + job) == -1:
        idcards += ",id_" + job
    SpawnPointHuman = {'job': job, 'x': x, 'y': y, 'idcardtags': idcards}
    return SpawnPointHuman


# things to import:
# Submarine name

# jobs to replace,  assistant split to other classes and awaiting rework
newJobs = [
    'commanding_officer', 'executive_officer', 'navigator', 'chief',
    'engineering', 'mechanical', 'quartermaster', 'head_of_security',
    'security', 'diver', 'chiefmedicaldoctor', 'medicalstaff', 'passenger',
    'janitor', 'inmate'
]
vanillaJobs = [
    'captain', 'engineer', 'mechanic', 'securityofficer', 'medicaldoctor',
    'assistant'
]

# seeted in main
# filename = "Azimuth [JE].xml"

# # seeted in main
# changename = False

def main():
    global filename
    global changename
    filename  = "Azimuth [JE].xml"
    changename = False
    if(len(sys.argv) > 1):
        for i in range(1,len(sys.argv)):
            # IndexError: string index out of range for some thus this:
            if(len(sys.argv[i]) > 4):
                if(str(sys.argv[i][-4]) + str(sys.argv[i][-3]) + str(sys.argv[i][-2]) + str(sys.argv[i][-1]) == '.sub' and os.path.exists(sys.argv[i])):
                    filename = sys.argv[i]
                    with gzip.open(filename, 'rb') as f:
                        file_content = f.read()
                # TODO support for more than one 'filename' or/and detect if user screwed up and typed sub twice. Also less supid check

                        filename = filename[:-4] + ".xml"
                        with open(filename, 'wb') as fx:
                                fx.write(file_content)

            if len(sys.argv) >= 3 :
                if sys.argv[2] == '--changename' or sys.argv[2] == '-c':
                    changename = True
    # else:
    # TODO a propt for user imput if no arguents are given

    # parse an xml file by name
    with minidom.parse(filename) as mydoc:
        items = mydoc.getElementsByTagName('Submarine')[0]

        requiredcontentpackages = items.getAttribute('requiredcontentpackages')
        name = items.getAttribute('name')
        description = items.getAttribute('description')
        #cant print this as variable so whatever
        previewimage = items.getAttribute('previewimage')

        # one specific item attribute
        print('Item name attribute: ' + name)
        print('Item description attribute: ' + description)
        print('Item requiredcontentpackages attribute: ' + requiredcontentpackages)

        previewimage = base64.b64decode(previewimage)
        name_ofpic = name + ".png"
        image_result = open(name_ofpic, 'wb')
        print("Item previewimage attribute: " + "In a file: " + name_ofpic)
        image_result.write(previewimage)

        # get all waypoints
        items = mydoc.getElementsByTagName('WayPoint')
        # all all original waypoints
        waypoints = []
        # maxofwaypoints = 0 not needed, use len(waypoints)
        lastID = 0

        # add classes to 'waypoints' array
        for elem in items:
            if elem.getAttribute("spawn") == "Human":
                job = elem.getAttribute('job')
                # initialized first to catch errors later
                x = 0
                y = 0
                idcards = "error"
                if job in vanillaJobs:
                    x = elem.getAttribute('x')
                    y = elem.getAttribute('y')
                    idcardtags = elem.getAttribute('idcardtags')
                    SpawnPointHuman = {
                        'job': job,
                        'x': x,
                        'y': y,
                        'idcardtags': idcardtags
                    }
                    waypoints.append(SpawnPointHuman)
            if int(elem.getAttribute("ID")) >= lastID:
                lastID = int(elem.getAttribute("ID")) + 1

        # remove all occurences of 'newJobs' hope it works
        for elem in items:
            if elem.getAttribute("spawn") == "Human":
                if elem.getAttribute('job') in newJobs:
                    mydoc.documentElement.removeChild(elem)
                    elem.unlink()

        # create new waypoints and store them in 'newwaypoints' array
        newwaypoints = []
        for i in range(len(waypoints)):
            offset = 40
            # capitan -> co + xo + nav
            if waypoints[i]['job'] == 'captain':
                # add co spawn from variables - same coordinates as capitan
                job = 'commanding_officer'
                newwaypoints.append(add_by_id(job, waypoints[i], 0))
                # add xo spawn from variables - coordinates from co x=x-2
                job = 'executive_officer'
                newwaypoints.append(add_by_id(job, waypoints[i], -offset))
                # add nav spawn from variables - coordinates from co x=x+2
                job = 'navigator'
                newwaypoints.append(add_by_id(job, waypoints[i], offset))
            
            # engineer -> engineering + chief
            if waypoints[i]['job'] == 'engineer':
                # add engineering spawn from variables - same coordinates as engineer
                job = 'engineering'
                newwaypoints.append(add_by_id(job, waypoints[i], 0))
                # add chief spawn from variables - coordinates from engineering x=x-2
                job = 'chief'
                newwaypoints.append(add_by_id(job, waypoints[i], -offset))
            
            # mechanic -> mechanical + quartermaster
            if waypoints[i]['job'] == 'mechanic':
                # add mechanical spawn from variables - same coordinates as mechanic
                job = 'mechanical'
                newwaypoints.append(add_by_id(job, waypoints[i], 0))
                # add quartermaster spawn from variables - coordinates from mechanical x=x-2
                job = 'quartermaster'
                newwaypoints.append(add_by_id(job, waypoints[i], -offset))
            
            # assistant -> passenger + janitor
            if waypoints[i]['job'] == 'assistant':
                # add passenger spawn from variables - same coordinates as assistant
                job = 'passenger'
                newwaypoints.append(add_by_id(job, waypoints[i], 0))
                # add janitor spawn from variables - coordinates from assistant x=x-2
                job = 'janitor'
                newwaypoints.append(add_by_id(job, waypoints[i], -offset))

            # securityofficer -> securityofficer + head_of_security + diver
            if waypoints[i]['job'] == 'securityofficer':
                # add security spawn from variables - same coordinates as previous
                job = 'security'
                newwaypoints.append(add_by_id(job, waypoints[i], 0))
                # add head_of_security spawn from variables - coordinates from securityofficer x=x-2
                job = 'head_of_security'
                newwaypoints.append(add_by_id(job, waypoints[i], -offset))
                # add diver spawn from variables - coordinates from securityofficer x=x+2
                job = 'diver'
                newwaypoints.append(add_by_id(job, waypoints[i], offset))
            
            # medicaldoctor -> medicaldoctor + chiefmedicaldoctor + passenger
            if waypoints[i]['job'] == 'medicaldoctor':
                # add medicalstaff spawn from variables - same coordinates as previous
                job = 'medicalstaff'
                newwaypoints.append(add_by_id(job, waypoints[i], 0))
                # add chiefmedicaldoctor spawn from variables - coordinates from medicaldoctor x=x-2
                job = 'chiefmedicaldoctor'
                newwaypoints.append(add_by_id(job, waypoints[i], -offset))
                # add passenger spawn from variables - coordinates from medicaldoctor x=x+2
                job = 'passenger'
                newwaypoints.append(add_by_id(job, waypoints[i], offset))


        # testing 'newwaypoints' array
        print('\n')
        for i in range(len(newwaypoints)):
            newWaypoint = mydoc.createElement('WayPoint')
            newWaypoint.setAttribute('ID', str(lastID))
            lastID = 1 + lastID
            newWaypoint.setAttribute('x', str(newwaypoints[i]['x']))
            newWaypoint.setAttribute('y', str(newwaypoints[i]['y']))
            newWaypoint.setAttribute('spawn', "Human")
            newWaypoint.setAttribute('idcardtags', str(newwaypoints[i]['idcardtags']))
            newWaypoint.setAttribute('job', str(newwaypoints[i]['job']))
            # testing 'newwaypoints' array
            print(newWaypoint.toxml())
            mydoc.documentElement.appendChild(newWaypoint)

        # change name option
        if changename and name.find(' [JE]') == -1:
            name = name + ' [JE]'
        mydoc.documentElement.setAttribute('name', name)
        # add JobsExtended to requiredcontentpackages
        if requiredcontentpackages.find('JobsExtended') == -1:
            requiredcontentpackages = requiredcontentpackages + ', JobsExtended'
        mydoc.documentElement.setAttribute('requiredcontentpackages', requiredcontentpackages)

        # all items data TESTING
        filenameoutput = name
        print('\nAll item data in: ' + filenameoutput)
        image_result = open(filenameoutput + ".xml", 'w')
        file_string = mydoc.toprettyxml(indent='   ', newl='')
        image_result.write(file_string)

        with open(filenameoutput  + ".xml", 'rb') as f:
            file_content = f.read()
        with gzip.open(filenameoutput + ".sub", 'wb') as f:
            f.write(file_content)

main()