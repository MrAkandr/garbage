import requests
import multiprocessing

#class for working with killmails
class killmails_handler():

    def thread_test(self, killmails):
        workers = int(len(killmails)/20)
        pool = multiprocessing.Pool(workers)
        result = pool.map(self.get_and_parce_esi_details, killmails)
        for x in result:
            print(str(x))


    def get_and_parce_esi_details(self, killmail):
        print('we in get and parce')
        return self.parse_esi_killmail_details(self.fetch_killmail_details(killmail[0], killmail[1]))

    # api call itself
    def api_call(self, url):
        return requests.get(url).json()

    # fetching information from api

    # by region
    def fetch_killmails_by_region(self, region_id):
        return self.api_call(string_handler().zbk_url_builder_killmails_by_region(region_id))

    # killmail details by id and hash

    def fetch_killmail_details(self, killmail_id, killmail_hash):
        return self.api_call(string_handler().esi_url_builder_killmail_details(killmail_id, killmail_hash))

    # character name by character id

    def fetch_character_name(self, character_id):
        return self.api_call(string_handler().esi_url_builder_character(character_id))

    # final killmail output ready to be analysed
    # by region

    def get_parced_killmails_by_region(self, region_id):
        zbk_killmails = self.parse_zbk_killmails(self.fetch_killmails_by_region(region_id))
        full_killmails = self.create_full_killmail_list_with_details(zbk_killmails)
        #create_full_killmail_list_with_details
        return full_killmails

    # parsing
    #parsing zbk responce
    def parse_zbk_killmails(self, api_responce_killmails):
        parced_killmails = []
        for killmail in api_responce_killmails:
            parced_killmails.append([killmail['killmail_id'], killmail['zkb']['hash']])
        return parced_killmails

    #parsing character responce
    def parse_character(self, api_response_character):
        return api_response_character['name']

    #parsing types responce
    def parse_ship_information(ship):
        return ship['name']

    # parse esi killmails responce
    def parse_esi_killmail_details(self, killmail):
        participant = []
        participants = []
        killmail_detail = []
        for atacker in killmail['attackers']:
            if 'character_id' not in atacker:
                character = 'npc'
            else:
                character = atacker['character_id']
            if 'ship_type_id' not in atacker:
                ship = 'ship not found'
            else:
                ship = atacker['ship_type_id']
            participant = [character, ship]
        participants.append(participant)
        killmail_detail.append(killmail['killmail_time'])
        killmail_detail.append(participants)
        return killmail_detail

    # final killmail data assembley

    def attach_details_to_killmail(self, killmails, killmail_details):
        count = 0
        finalList = []
        for killmail in killmails:
            killmail.append(killmail_details[count])
            count = count + 1
            finalList.append(killmail)
        return finalList

    # create list of killmails with details

    def create_full_killmail_list_with_details(self, killmails):
        count = 0
        details = []
        for killmail in killmails:
            details.append(self.parse_esi_killmail_details(self.fetch_killmail_details(killmail[0], killmail[1])))
            count = count + 1
        return self.attach_details_to_killmail(killmails, details)

#for building urls for api calls
class string_handler():
    #first part of zbk url
    def url_builder_zbk(self, next_url_part):
        return 'https://zkillboard.com/api/kills/' + next_url_part

    #first part of esi url
    def url_builder_esi(self, next_url_part):
        return 'https://esi.evetech.net/latest/' + next_url_part

    #complete url for zbk request to search by region
    def zbk_url_builder_killmails_by_region(self, region_id):
        return self.url_builder_zbk('regionID/' + str(region_id) + '/')

    #complete url for esi request to get killmail details
    def esi_url_builder_killmail_details(self, killmail_id, killmail_hash):
        return self.url_builder_esi('killmails/' + str(killmail_id) + '/' + str(killmail_hash) + '/')

    #complete url for esi request to get character name by id
    def esi_url_builder_character(self, character_id):
        return self.url_builder_esi('characters/' + str(character_id) + '/')

    #complete url for esi request to get information about id
    def esi_url_builder_types(self, type_id):
        return self.url_builder_esi('universe/types/' + str(type_id) + '/')


class checker():
    def is_ship_in_group_we_look_for(self, ship_id, ship_to_look_for):
        for ship_id in ship_to_look_for:
            if str(ship_id) == str(ship_id):
                return True
            else:
                return False

    def get_atackers_we_look_for(self, killmail, ships_to_look_for):
        atackers = killmail[2]
        atackers_we_look_for = []
        for atacker in atackers[1]:
            if str(atacker[0]) != 'npc':
                if self.is_ship_in_group_we_look_for(atacker[1], ships_to_look_for) == True:
                    atackers_we_look_for.append(atacker[0])
        return atackers_we_look_for


class file_handler():

    def read_file(self, file):
        ships_ids = []
        with open(file) as file_with_ids:
            for line in file_with_ids:
                ships_ids.append(self.file_parse_line(line))
                if 'str' in line:
                    break
        return ships_ids

    def file_parse_line(self, line):
        return line.split(" ")[0].replace("\n", "")

    def read_ships_file(self):
        return self.read_file('ships_id.txt')


# test
def compose_list_of_possible_cyno_characters(killmails):
    cynocharacters = []
    for killmail in killmails:
        characters = checker().get_atackers_we_look_for(killmail, file_handler().read_ships_file())
        if not characters:
            bla = 0
        else:
            cynocharacters.append(characters)
    for x in cynocharacters:
        for y in x:
            print(killmails_handler().parse_character(killmails_handler().fetch_character_name(y)))


x = killmails_handler()
#kills = x.get_parced_killmails_by_region(10000048)
#compose_list_of_possible_cyno_characters(kills)
zbk_killmails = x.parse_zbk_killmails(x.fetch_killmails_by_region(10000048))
if __name__ == '__main__':
    x.thread_test(zbk_killmails)
