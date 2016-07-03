import sqlite3
from hn_search_api_helpers import get_thread_data_by_user, \
get_comments_from_thread, dump_json_file
from settings import DATABASE_NAME
import datetime
import re
from bs4 import BeautifulSoup
import sys
from finding_location import check_line_for_location
'''
Functions that are used for updating the DB
'''

def get_max_db_id():
    '''
    returns: max id from the posts table
    '''
    #db = sqlite3.connect(DATABASE_NAME)
    db = sqlite3.connect('../test_db/testDB12.db')
    
    sql_command = 'SELECT MAX(id) FROM posts'
    cursor = db.execute(sql_command)
    max_id = cursor.fetchone()[0]
    return max_id
    
def get_current_month_comments():
    '''
    first gets Who is Hiring? thread from current month
    then gets the comments for that thread
    returns: comments as json list of dicts
    '''
    current_date = datetime.date.today().replace(day=1)
    current_date_iso = current_date

    threads = get_thread_data_by_user('whoishiring')
    for thread in threads:
        if thread['created'] == current_date_iso:
            current_thread = thread
            break
    else:
        raise KeyError('Current month thread not found')
    
    comments = get_comments_from_thread(thread)
    return comments
    
def select_new_comments(comments, max_db_id):
    '''
    given: comments and max_db_id
    returns: comments that have higher id than max_db_id
    '''
    new_comments = []
    for comment in comments:
        if comment['id'] > max_db_id:
            new_comments.append(comment.copy())
    return new_comments
    
def guess_company(comment):
    '''
    given: comment
    Looks if first line has delimeters | or -
    If so it takes everything up to the first non-alphanumeric (allowing periods)
    If not it will return None
    Returns the company name
    '''

    soup = BeautifulSoup(comment['text'], "html.parser") 
        
    first_line = soup.findAll('p')[0]
    first_line = ' '.join(first_line.findAll(text=True))
    
    if not first_line:
        return None
    
    if '|' not in first_line and '-' not in first_line:
        return None
    
    # only need to do this split if want to check if first section matches a location...    
    # p = re.compile('[|-]')
    # first_section = p.split(first_line)[0]
    
    p = re.compile('[\w \.]+')
    m = p.match(first_line)
    if m:
        company_guess = m.group()

        loc_line, possible_locs = check_line_for_location(company_guess)
    
        # ignore if it completely matches a location
        # loc_line has location replaced with spaces, so use strip to 
        # see if it is all spaces
        if possible_locs and len(loc_line.strip() == 0):
            return None
            

    # found_locs = check_line_for_location(first_line)
    # print found_locs
    # if comment['id'] in id_to_locations:
    #     print id_to_locations[comment['id']]
    # r = raw_input()
    # if r == 'q':
    #     sys.exit()
    
    
def main_update():
    '''
    Main function for updating db
    '''
    max_db_id = get_max_db_id()
    
    comments = get_current_month_comments()
    # [{id, thread_id, text, thread_date, comment_date}]
    
    new_comments = select_new_comments(comments, max_db_id)
    
    for comment in new_comments:
        guess_company(comment)
        #r = raw_input()
        #if r== 'q':
        #    sys.exit()
    
    # best guess at company name and location
    
    # get google location data
    
    # get glassdoor data
        # - first get all urls in post to compare to glassdoor
    
    # update databases
    
    #dump_json_file(comments, 'July_2016_comments.json')
main_update()