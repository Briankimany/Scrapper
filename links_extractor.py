

import numpy as np

def fmovies(data):
    def get_links(data):
        try:
            related_items = data.find("div" , class_ = "scaff top9 related items")
            if related_items:
                related_items= related_items.find_all("a" , class_ = "item")
            else:
                print("Encountered an issue")
                return {} , {}
            links_ = [data.host_link + i['href'] for i in related_items]
            image_link_to_name  = [(  i.find("img")['data-src'] ,i.find("img")['alt']  )  for i in related_items]
            names = list(np.array(image_link_to_name)[:,1])
            redirect_links = list(zip(links_ , names))

            menu_items = data.find("div" , id="menu").find_all("a")
            
            if menu_items:
                redirect_links += [(data.host_link  + i['href'] , i.text) for i in menu_items]
            
            return  dict(redirect_links) , dict(image_link_to_name)
        except Exception as e:
            print(f"Got an error: {str(e)}")
            return {} , {}
    return get_links(data=data)
