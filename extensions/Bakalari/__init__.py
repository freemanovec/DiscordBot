import urllib3, json, sys, re, datetime
from bs4 import BeautifulSoup as BS

pool = urllib3.PoolManager()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_current_week_info(debug = False):
    #1st POST on is.sssvt.cz/IS/websssvt.aspx #1090
    #old:
    #   #nothing, everything dumped
    #new:
    #   #on the request:
    #       baklogid (pass)
    #       bkapptype (pass)
    #       bakauvod (pass)
    #   #on response:
    #       ASP.NET_SessionId (pass)
    #       HttpOnly (just key, pass)
    if debug: print("Part 4 - 1st POST is.sssvt.cz/IS/websssvt.aspx")

    url = "is.sssvt.cz/IS/websssvt.aspx"
    with open('extensions/configurations/private/bakalari_username') as usernameFile:
        username = usernameFile.read().strip()
    with open('extensions/configurations/private/bakalari_password') as passwordFile:
        password = passwordFile.read().strip()
    raw_cookies = "baklogid=https://is.sssvt.cz/IS/websssvt.aspx; bkapptype=OLD; bakauvod=%7B%22upozorneni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C1%5D%2C%22suplovani%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C3%5D%2C%22DateTime2%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22400%22%2C%220%22%2C0%2C0%2C5%5D%2C%22kontakty%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C6%5D%2C%22prihlaseni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C7%5D%7D; _gat=1; _dc_gtm_UA-2995187-1=1; _ga=GA1.2.1606626948.1509919094; _gid=GA1.2.1741393958.1509919094"
    response = pool.request(
        "POST",
        url,
        fields={
            "polickojmeno": username,
            "polickoheslo": password
        },
        headers={
            "Cookie": raw_cookies
        }
    )
    status = response.status
    headers = response.headers
    data = response.data
    if debug: print(status)
    if debug: print(headers)
    data_conjoined = "".join(map(chr, data))
    if debug: print("1. pololet" in data_conjoined) #as in pcap

    asp_net_sessionid = headers["Set-Cookie"].split("=")[1].split(";")[0]
    if debug: print(asp_net_sessionid)

    #2nd POST on is.sssvt.cz/IS/webssvt.aspx #1107
    #old:
    #   ASP.NET_SessionId (pass)
    #new:
    #   #on the request:
    #       baklogid (pass)
    #       bkapptype (pass)
    #       bakauvod (pass)
    #   #on response:
    #       #302 to /IS/uvod.aspx
    #       bkapptype
    if debug: print("Part 5 - 2nd POST is.sssvt.cz/IS/websssvt.aspx")

    url = "is.sssvt.cz/IS/websssvt.aspx"
    raw_cookies = "baklogid=https://is.sssvt.cz/IS/websssvt.aspx; bkapptype=OLD; bakauvod=%7B%22upozorneni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C1%5D%2C%22suplovani%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C3%5D%2C%22DateTime2%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22400%22%2C%220%22%2C0%2C0%2C5%5D%2C%22kontakty%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C6%5D%2C%22prihlaseni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C7%5D%7D; _gat=1; _dc_gtm_UA-2995187-1=1; _ga=GA1.2.1606626948.1509919094; _gid=GA1.2.1741393958.1509919094; ASP.NET_SessionId=" + asp_net_sessionid
    response = pool.request(
        "POST",
        url,
        fields={
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": "/wEPDwUKMjA0OTQ0MTQ5Nw9kFgJmD2QWAgIDD2QWAgIBD2QWEGYPZBYCAgEPDxYEHghJbWFnZVVybAUNaW1hZ2VzL2NzLnBuZx4HVG9vbFRpcAUNWm3Em25hIGphenlrYWRkAgEPDxYCHgRUZXh0BQp1xb5pdmF0ZWw6ZGQCAg8PFgIfAgUJb2RobMOhc2l0ZGQCAw8PFgIfAgUHam3DqW5vOmRkAgQPDxYCHgdWaXNpYmxlaGRkAgUPDxYCHwNoZGQCBw9kFhwCAQ8PFgIfAgUOUMWZaWhsw6HFoWVuw61kZAICDw8WAh8CBRdQxZlpaGxhxaFvdmFjw60gam3DqW5vOmRkAgQPDxYCHwIFBkhlc2xvOmRkAgUPDxYCHwNoZBYCAgEPDxYCHwIFEXphcG9tZW51dMOpIGhlc2xvZGQCBg8PFgIfA2hkZAIIDw8WAh8CBQpVxb5pdmF0ZWw6ZGQCCQ8QZGQWAGQCCg8QZGQWAGQCDA8PFgIfA2hkZAINDzwrAAYBAA8WAh8CBQtQxZlpaGzDoXNpdGRkAg4PDxYCHwNoZGQCDw8PFgYfAgUjUMWZaWhsw6FzaXQgc2UgcG9tb2PDrSBXaW5kb3dzIExpdmUeC05hdmlnYXRlVXJsZR8DaGRkAhAPPCsABAEADxYEHwIFF1rFr3N0YXQgcMWZaWhsw6HFoWVuKGEpHwNoZGQCFA88KwAIAQAPFgIeDl8hVXNlVmlld1N0YXRlZ2RkAggPPCsACAIADxYCHwVnZAY8KwASAQAWAh4KSGVhZGVyVGV4dAUNWm3Em25hIGphenlrYWQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgYFG2N0bDAwJGNwaG1haW4kQnV0dG9uUHJpaGxhcwUXY3RsMDAkY3BobWFpbiRwb3B1cDJvb20FC2N0bDAwJHBvcHVwBRFjdGwwMCRwb3B1cCRpbWdjcwURY3RsMDAkcG9wdXAkaW1nZW4FEWN0bDAwJHBvcHVwJGltZ2ZyrQMaL8PUOdW30ERD3uaGfqRtVhsQa2tCiyb0N08YgKU=",
            "__VIEWSTATEGENERATOR": "94561C5F",
            "ctl00$cphmain$Loginname": username,
            "ctl00$cphmain$Loginname1": "",
            "ctl00$cphmain$Loginname2": "",
            "ctl00$cphmain$TextBoxHeslo": password,
            "ctl00$cphmain$ButtonPrihlas": "Přihlásit",
            "ctl00$popup$checklexpredmety": "U"
        },
        headers={
            "Cookie": raw_cookies
        },
        retries=False
    )
    status = response.status
    headers = response.headers
    data = response.data
    if debug: print(status)
    if debug: print(headers)

    #GET /IS/uvod.aspx #1176
    #old:
    #   ASP.NET_SessionID (pass)
    #   baklogid (pass)
    #   bkapptype (pass)
    #new:
    #   set bkapptype to OLD
    if debug: print("Part 6 - GET to is.sssvt.cz/IS/uvod.aspx")

    url = "is.sssvt.cz/IS/uvod.aspx"
    raw_cookies = "bakauvod=%7B%22upozorneni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C1%5D%2C%22suplovani%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C3%5D%2C%22DateTime2%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22400%22%2C%220%22%2C0%2C0%2C5%5D%2C%22kontakty%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C6%5D%2C%22prihlaseni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C7%5D%7D; _gat=1; _dc_gtm_UA-2995187-1=1; _ga=GA1.2.1606626948.1509919094; _gid=GA1.2.1741393958.1509919094; ASP.NET_SessionId=" + asp_net_sessionid + "; baklogid=https://is.sssvt.cz/IS/websssvt.aspx; bkapptype=OLD"
    response = pool.request(
        "GET",
        url,
        headers={
            "Cookie": raw_cookies
        }
    )
    status = response.status
    headers = response.headers
    data = response.data
    if debug: print(status)
    if debug: print(headers)
    data_conjoined = "".join(map(chr, data))
    splitted = data_conjoined.splitlines()
    the_line = ""
    for line in splitted:
        #if("dxpc-link" in line and "prehled.aspx" in line):
        #    the_line = line.strip()
        if("prehled.aspx" in line and "Rozvrh" in line):
            the_line = line.strip()

    ref = ""
    if debug: print(the_line)
    bs = BS(the_line, "lxml")
    for item in bs.find_all("a"):
        if(item.find("font").find("span").getText() == "Rozvrh"):
            ref = item["href"]
        #print(item)
    if debug: print(ref)

    if debug: print("Part 7 - GET to is.sssvt.cz/IS/" + ref)

    url = "is.sssvt.cz/IS/" + ref
    raw_cookies = "_gat=1; _dc_gtm_UA-2995187-1=1; _ga=GA1.2.1606626948.1509919094; _gid=GA1.2.1741393958.1509919094; ASP.NET_SessionId=" + asp_net_sessionid + "; baklogid=https://is.sssvt.cz/IS/websssvt.aspx; bkapptype=OLD; bakauvod=%7B%22upozorneni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C1%5D%2C%22suplovani%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C3%5D%2C%22DateTime2%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22400%22%2C%220%22%2C0%2C0%2C5%5D%2C%22kontakty%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C6%5D%2C%22prihlaseni%22%3A%5Btrue%2C%22All%22%2C%22LeftZone%22%2C%22270%22%2C%220%22%2C0%2C0%2C7%5D%7D"
    response = pool.request(
        "GET",
        url,
        headers={
            "Cookie": raw_cookies
        }
    )
    status = response.status
    headers = response.headers
    data = response.data
    if debug: print(status)
    if debug: print(headers)
    data_conjoined = "".join(map(chr, data))
    if debug: print("cphmain_Panelrozvrh" in data_conjoined)

    bs = BS(data_conjoined, "lxml")
    super_table = bs.find("table", class_="r_roztable")
    if debug: print(super_table != None)
    table = super_table.find("tbody")
    if debug: print(table != None)
    all_rows = table.find_all("tr")
    if debug: print(all_rows != None)
    if debug: print(len(all_rows))
    if(len(all_rows) != 6):
        print("Weird table or the amount of days in a week changed")
        return None
    days = {
        0: ["Monday","Pondělí"],
        1: ["Tuesday", "Úterý"],
        2: ["Wednesday", "Středa"],
        3: ["Thursday", "Čtvrtek"],
        4: ["Friday", "Pátek"]
    }
    all_data = []
    for i in range(5):
        current_row = all_rows[i+1]
        current_day = days[i][0]
        if debug: print("Current day: {}".format(current_day))
        all_fields = current_row.find_all("td")
        current_day_details = []
        for j in range(len(all_fields)):
            #Keys:
            #   Type        field_type
            #   Predmet     field_lesson
            #   Ucitel      field_teacher
            #   Ucebna      field_classroom
            #   Skupina     field_group
            field = all_fields[j]

            cs = field["class"][0]
            if(cs == "r_rozden"):
                continue
            field_type = "WTF"
            if(cs == "r_rrzm"):
                field_type = "Changed"
            elif(cs == "r_rrw"):
                field_type = "Classic"
            elif(cs == "r_rr"):
                field_type = "Free"
            
            if(field_type == "Free"):
                field_lesson = "None"
            else:
                inner_div = field.find("div", {"class": lambda L: L and L.startswith("r_bunka")})
                more_inner_div = inner_div.find("div", class_="r_predm")
                predmet_div = more_inner_div.find("span", class_="tkspan")
                if(predmet_div == None):
                    field_lesson = more_inner_div.contents[0]
                else:
                    field_lesson = predmet_div.contents[0]

            if(field_type == "Free"):
                field_teacher = "None"
            else:
                inner_div = field.find("div", {"class": lambda L: L and L.startswith("r_bunka")})
                field_teacher = inner_div.find("div", class_="r_ucit")["title"]
                field_teacher = field_teacher.encode('latin1').decode('utf8')

            if(field_type == "Free"):
                field_classroom = "None"
            else:
                inner_div = field.find("div", {"class": lambda L: L and L.startswith("r_bunka")})
                field_classroom = inner_div.find("div", class_="r_mist").find("div", class_="r_dole").contents[0]

            if(field_type == "Free"):
                field_group = "None"
            else:
                try:
                    inner_div = field.find("div", {"class": lambda L: L and L.startswith("r_bunka")})
                    field_group = inner_div.find("div", class_="r_skup").find("div", class_="r_dolel").contents[0]
                except:
                    field_group = "None"

            current_day_details.append({
                "type": field_type,
                "lesson": field_lesson,
                "teacher": field_teacher,
                "classroom": field_classroom,
                "group": field_group
            })
        all_data.append(current_day_details)
    return all_data

def get_changes_current_day(week_info):
    current_day = datetime.datetime.today().weekday()
    #current_day = 0 #to simulate Monday
    changes = []
    days = {
        0: ["Monday","Pondělí"],
        1: ["Tuesday", "Úterý"],
        2: ["Wednesday", "Středa"],
        3: ["Thursday", "Čtvrtek"],
        4: ["Friday", "Pátek"]
    }
    if(current_day not in range(5)):
        print("Not a work-day (#{})".format(current_day))
        return
    day_info = week_info[current_day]
    for i in range(len(day_info)):
        lesson = day_info[i]
        if(lesson["type"] == "Changed"):
            text = "Změna v rozvrhu: {}, {}. hodina, bude vyučovat {} předmět {} v učebně {}".format(
                days[i][1],
                i+1,
                lesson["teacher"],
                lesson["lesson"],
                lesson["classroom"]
            )
            changes.append(text)
    return changes

if(__name__ != "__main__"):
    print("Using extension: Bakalari")
