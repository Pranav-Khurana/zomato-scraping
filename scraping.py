import json
import pandas as pd
from selenium import webdriver

# GET THE LINKS OF FIRST 100 RESTAURANTS
def get_links():
    i = 1
    links = []
    base_url = "https://www.zomato.com/agra/restaurants?page="
    while len(links) < 100:
        url = base_url + str(i)
        content = driver.get(url)
        results = driver.find_elements_by_class_name("result-title")
        places = [result.get_attribute('href') for result in results]
        links.extend(places)
        i += 1
    return links

# GET ALL THE JSON DATA OF THE PAGE
def get_json(link):
    driver.get(link)
    data = driver.find_element_by_xpath('/html/body/script[2]').get_attribute('innerHTML')
    data = data.replace("\\", "")
    final_data = data.split('JSON.parse("', 1)[0]
    final_data = final_data.split(',"SECTION_RATING_HISTOGRAM":')[1]
    final_data = final_data + '}}}}}'
    json_data = json.loads(final_data)
    return json_data

# PARSE ALL THE JSON DATA
def parse_json(json_data):
    resid = json_data['pages']['current']['resId']

    base_info = json_data['pages']['restaurant'][str(resid)]['sections']['SECTION_BASIC_INFO']
    name = base_info['name']
    cuisine = base_info['cuisine_string']
    dine_rating = base_info['rating_new']['ratings']['DINING']['rating']
    del_rating = base_info['rating_new']['ratings']['DELIVERY']['rating']
    timing = base_info['timing']['customised_timings']['opening_hours'][0]['timing'].replace('u2013', '-')
    days = base_info['timing']['customised_timings']['opening_hours'][0]['days']

    res_info = json_data['pages']['restaurant'][str(resid)]['sections']['SECTION_RES_DETAILS']
    known_for = res_info['KNOWN_FOR']['knownFor']
    try:
        people_like = res_info['PEOPLE_LIKED']['description']
    except:
        people_like = None
    top_dishes = res_info['TOP_DISHES']['description']
    avg_cost = res_info['CFT_DETAILS']['cfts'][0]['title']
    temp_high = res_info['HIGHLIGHTS']['highlights']
    highlights = ''
    for val in temp_high:
        highlights = highlights + val['text'] + ', '
    
    
    res_contact = json_data['pages']['restaurant'][str(resid)]['sections']['SECTION_RES_CONTACT']
    address = res_contact['address']
    phone = res_contact['phoneDetails']['phoneStr']

    new_row = {
        'RESID': resid, 'NAME': name, 'ADDRESS': address, 'CONTACT': phone, 'TIMINGS': timing, 'DAYS OPEN': days,
        'CUISINE': cuisine, 'DINING RATING': dine_rating, 'DELIVERY RATING': del_rating, 'KNOWN FOR': known_for,
        'PEOPLE LIKED': people_like, 'TOP DISHES': top_dishes, 'HIGHLIGHTS': highlights, 'AVERAGE COST': avg_cost
    }
    return new_row


if __name__ == "__main__":

    # CREATING THE DATAFRAME
    zomato_data = pd.DataFrame(
        columns=['RESID', 'NAME', 'ADDRESS', 'CONTACT', 'TIMINGS', 'DAYS OPEN',
                 'CUISINE', 'DINING RATING', 'DELIVERY RATING', 'KNOWN FOR',
                 'PEOPLE LIKED', 'TOP DISHES', 'HIGHLIGHTS', 'AVERAGE COST'])

    # TRYING TO SET UP NETWORK PROXY (NOT SURE IT IS WORKING OR NOT)
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    #profile.set_preference('network.proxy.socks_port', 9150)
    driver = webdriver.Firefox(profile)

    # LIST OF LINKS OF FIRST 100 RESTAURANTS
    links = get_links()

    for link in links:
        try:
            json_data = get_json(link)
            new_row = parse_json(json_data)
            zomato_data = zomato_data.append(new_row, ignore_index=True)
        except:
            pass


    zomato_data.to_csv('/home/pranav/Desktop/Internship/zomato.csv', index=False)

    driver.quit()
