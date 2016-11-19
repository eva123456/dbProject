from django.shortcuts import render
from django.http import HttpResponse, QueryDict
from django.db import connection
import mysql.connector
from mysql.connector import Error
from django.db import IntegrityError, ProgrammingError, OperationalError
from django.core import serializers
from itertools import *
from django.views.decorators.csrf import csrf_exempt
import json
import MySQLdb
from django.http import JsonResponse
import ast

#Connection to database
db = MySQLdb.connect("localhost","root","f66n9zae2f","API",charset='utf8', init_command='SET NAMES UTF8')
db.set_character_set('utf8')
dbc = db.cursor()
dbc.execute('SET Names utf8;')
dbc.execute('set character set utf8;')
dbc.execute('set character_set_connection=utf8;')
dbc.execute("SET SESSION collation_connection = 'utf8_general_ci';")
db.commit()


def set_quots(data):
    quots_str = "'" + '%s' % data + "'"
    return quots_str


@csrf_exempt
def create(request):
    code = 0
    url = request.path
    table = url.replace('/db/api/','').replace('/create','').replace('/','').capitalize()
    params = request.body
    params = ast.literal_eval(request.body)
    cursor = db.cursor()

    if 'user' in params.keys():
        email = set_quots(params['user'])
        subquery = 'SELECT idUser FROM User WHERE email = ' + email +';'
        cursor.execute(subquery)
        params['user'] = cursor.fetchone()[0]

    if 'forum' in params.keys():
        short_name = set_quots(params['forum'])
        subquery = 'SELECT idForum FROM Forum WHERE short_name = ' + short_name + ';'
        cursor.execute(subquery)
        params['forum'] = cursor.fetchone()[0]

    values = [set_quots(x) for x in params.values()]
    query = 'INSERT INTO {0}({1}) VALUES('.format(table, ', '.join(params.keys())) + ', '.join(values) + ');'

    cursor.execute(query)
    db.commit()

    key = params.keys()[0]
    value = set_quots(params[key])
    response = get_details(table, key, value)

    dictionary = {'code' : code, 'response' : response}
    return JsonResponse(dictionary)

def get_details(table, key, value):
    response = {}
    query = 'SHOW COLUMNS FROM {}'.format(table)
    cursor = connection.cursor()
    cursor.execute(query)
    columns = cursor.fetchall()
    keys = [columns[j][0] for j in range(len(columns))]

    query = 'SELECT {0} FROM {1} WHERE {2} = '.format(', '.join(keys), table, key) + value + ';'
    cursor.execute(query)
    data = cursor.fetchone()
    response = dict(izip(keys, data))
    if (response.has_key('date')):
        response['date'] = str(response['date'])

    id_val = response.pop('id'+table)
    response['id'] = id_val

    return response




'''
def create_entity(table, params):
    cursor = connection.cursor()
    code = 0
    response = {}

    try:
        creation_info = json.loads(request.body)
            try:
                cursor = connection.cursor()
            except:
                code = 4
                response = 'Unknown Error'
            try:
                strings = []
                for value in creation_info.values():
                    if(type(value) == bool):
                        value = 'true' if(value == True) else 'false'
                    if(type(value) == int):
                        value = str(value)
                    strings.append('%r'%value.encode('utf8'))
                query = 'INSERT INTO {0}({1}) VALUES({2})'.format(table, ', '.join(creation_info.keys()),', '.join(strings))
                cursor.execute(query)
                value = creation_info[keyField].encode('utf8')
                response = Get_details(request, table, keyField, value, fields)#only some fields
                if(table == 'Posts'):
                    subquery = 'UPDATE Threads SET posts = posts+1 where id = {}'.format(int(response['thread']))
                    cursor.execute(subquery)

            except IntegrityError:
                code = 5
                if(table == 'Users'):
                    response = 'This user is already exists'
                else:
                    value = creation_info[keyField].encode('utf8')
                    response = Get_details(request, table, keyField, value, fields)#only some fields
            except (ProgrammingError, OperationalError):
                code = 3
                response = 'Synopsys Error'
        except ValueError:
            code = 2
            response = 'Validation Error'
        finally:
            connection.close()
        dictionary = {'code': code, 'response': response }
        return dictionary

users_fieds = ['about','email','id','isAnonymous','name','username']
forum_fields = ['id','name','short_name','user']
post_fields = ['date','forum','id','isApproved','isDeleted','isEdited','isHighlighted','isSpam','message','parent','thread','user']
thread_fields = ['date','forum','id','isClosed','isDeleted','message','slug','title','user']

@csrf_exempt
def Clear(request):
    cursor = connection.cursor()
    cursor.execute('DELETE FROM Posts')
    cursor.execute('DELETE FROM SubscriptionsTable')
    cursor.execute('DELETE FROM Threads')
    cursor.execute('DELETE FROM Forums')
    cursor.execute('DELETE FROM FollowingTable')

    cursor.execute('DELETE FROM Users')
    connection.close()
    dictionary = {'code' : 0, 'response': 'OK'}
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Status(request):
    code = 0
    response = {}
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM Users')
    response['user'] = int(cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM Threads where isDeleted = false')
    response['thread'] = int(cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM Forums')
    response['forum'] = int(cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM Posts where isDeleted = false')
    response['post'] = int(cursor.fetchone()[0])
    dictionary = {'code': code, 'response': response}
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def User_create(request):
    dictionary = Create(request, 'Users', 'email',users_fieds)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Forum_create(request):
    dictionary = Create(request, 'Forums', 'user',forum_fields)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_create(request):
    dictionary = Create(request, 'Threads', 'user',thread_fields)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Post_create(request):
    dictionary = Create(request, 'Posts', 'user',post_fields)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

def User_details(request):
    code = 0
    value = request.GET.values()
    response = Get_details(request, 'Users', 'email',value[0].encode('utf8'))#all fields
    dictionary = {'code': code, 'response' : response}
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

def Forum_details(request):
    code = 0
    params = dict(request.GET.iterlists())
    required = params.get('forum',())
    possible = {'user':'email'}
    response = Get_details(request, 'Forums', 'short_name', required[0].encode('utf8'))
    optional = Get_optional(request, possible, 'Forums', 'short_name', required[0].encode('utf8'))
    response.update(optional)

    dictionary = {'code': code, 'response' : response}
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

def Thread_details(request):
    code = 0
    params = dict(request.GET.iterlists())
    required = params.get('thread',())
    possible = {'user':'email','forum':'short_name'}
    response = Get_details(request, 'Threads', 'id', required[0].encode('utf8'))
    optional = Get_optional(request, possible, 'Threads', 'id', required[0].encode('utf8'))
    response.update(optional)

    dictionary = {'code': code, 'response' : response}
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

def Post_details(request):
    code = 0
    params = dict(request.GET.iterlists())
    required = params.get('post',())
    possible = {'user':'email','forum':'short_name', 'thread':'id'}
    response = Get_details(request, 'Posts', 'id', str(required[0]).encode('utf8'))
    optional = Get_optional(request, possible, 'Posts', 'id', str(required[0]).encode('utf8'))
    response.update(optional)

    dictionary = {'code': code, 'response' : response}
    return HttpResponse(json.dumps(dictionary), content_type='application/json')


@csrf_exempt
def User_updateProfile(request):
    dictionary = update(request,'Users','user','email')
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Post_Vote(request):
    dictionary = Vote(request, 'Posts','post')
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Vote(request):
    dictionary = Vote(request, 'Threads','thread')
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Post_Update(request):
    dictionary = update(request, 'Posts', 'post', 'id')
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Post_Remove(request):
    dictionary = DeleteOrNot(request,'Posts', 'post', True)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Post_Restore(request):
    dictionary = DeleteOrNot(request,'Posts','post', False)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Remove(request):
    dictionary = DeleteOrNot(request,'Threads','thread', True)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Restore(request):
    dictionary = DeleteOrNot(request,'Threads','thread', False)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Close(request):
    dictionary = OpenOrClose(request,'thread',True)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Open(request):
    dictionary = OpenOrClose(request,'thread', False)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Update(request):
    dictionary = update(request, 'Threads', 'thread', 'id')
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Subscribe(request):
    dictionary = subscribeOrNot(request, True)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_Unsubscribe(request):
    dictionary = subscribeOrNot(request, False)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def User_Follow(request):
    dictionary = followOrNot(request, True)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def User_Unfollow(request):
    dictionary = followOrNot(request, False)
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_List(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'forum'
    required = params.get(key,())
    if( len(required) == 0):
        key = 'user'
        required = params.get(key,())
    required = str(required[0]).encode('utf8')
    response = Get_list(request, 'Threads', key, required)
    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Post_List(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'forum'
    required = params.get(key,())
    if( len(required) == 0):
        key = 'thread'
        required = params.get(key,())
    required = str(required[0]).encode('utf8')
    response = Get_list(request, 'Posts', key, required)
    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Thread_ListPosts(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'thread'
    required = params.get(key,())
    required = str(required[0]).encode('utf8')
    response = Get_list(request, 'Posts', key, required)
    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Forum_ListPosts(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'forum'
    required = params.get(key,())
    required = str(required[0]).encode('utf8')
    response = Get_list(request, 'Posts', key, required)
    #optional 'related' parametr
    possible = {'user':'email','forum':'short_name','thread':'id'}
    for d in response:
         subdict = Get_optional(request, possible, 'Posts', 'id', int(d['id'])) #d['id']????
         d.update(subdict)

    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Forum_ListThreads(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'forum'
    required = params.get(key,())
    required = str(required[0]).encode('utf8')
    response = Get_list(request, 'Threads', key, required)
    #optional 'related' parametr
    possible = {'user':'email','forum':'short_name'}
    for d in response:
        subdict = Get_optional(request, possible, 'Threads', 'id', int(d['id'])) #d['id']????
        d.update(subdict)

    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def Forum_ListUsers(request):
    code = 0
    response = []
    params = dict(request.GET.iterlists())
    key = 'forum'
    required = params.get(key,())
    required = str(required[0]).encode('utf8')

    #optional parametrs
    since_id = params.get('since_id',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())

    sinceQuery = ''
    limitQuery = ''

    if (since_id):
        since_id = since_id[0].encode('utf8')
        sinceQuery = 'AND u.id > {}'.format('%r'%since_id)
    if (limit):
        limit = limit[0]
        limitQuery = 'LIMIT {}'.format(int(limit)) #?

    order = order[0].encode('utf8')
    orderQuery = 'ORDER BY u.name {}'.format(order)
    condition = 'u.email = p.user'
    query = 'SELECT email FROM Users u, Posts p WHERE {0}={1} AND {2} {3} {4} {5}'.format(key, '%r'%required, condition, sinceQuery, orderQuery, limitQuery)
    cursor = connection.cursor()
    cursor.execute(query)
    emails = cursor.fetchall()
    for i in range(len(emails)):
        response.append(Get_details(request, 'Users', 'email', str(emails[i][0])))

    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def User_ListPosts(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'user'
    required = params.get(key,())
    required = str(required[0]).encode('utf8')
    response = Get_list(request, 'Posts', key, required)
    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def User_ListFollowers(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'user'
    required = params.get(key,())
    required = str(required[0]).encode('utf8')
    args = {'table':'FollowingTable','key':'followers','value': required }
    response = Get_listF(request, args)
    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

@csrf_exempt
def User_ListFollowing(request):
    code = 0
    params = dict(request.GET.iterlists())
    key = 'user'
    required = params.get(key,())
    required = str(required[0]).encode('utf8')
    args = {'table':'FollowingTable','key':'following','value': required }
    response = Get_listF(request, args)
    dictionary = {'code': code, 'response': response }
    return HttpResponse(json.dumps(dictionary), content_type='application/json')

#===================================================================================================================

def Get_listF(request, parametr):
    response = []
    cursor = connection.cursor()
    #optional parametrs
    params = dict(request.GET.iterlists())
    since_id = params.get('since_id',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())

    sinceQuery = ''
    limitQuery = ''
    if (since_id):
        since_id = since_id[0].encode('utf8')
        sinceQuery = 'AND id > {}'.format('%r'%since_id)
    if (limit):
        limit = limit[0]
        limitQuery = 'LIMIT {}'.format(int(limit)) #?

    order = order[0].encode('utf8')
    orderQuery = 'ORDER BY name {}'.format(order)
    subquery = '(SELECT email FROM {0} WHERE {1} = {2})'.format(parametr['table'], parametr['key'], '%r'%parametr['value'])
    query = 'SELECT email FROM Users WHERE email in {0} {1} {2} {3}'.format(subquery, sinceQuery, orderQuery, limitQuery)
    cursor.execute(query)
    ids = cursor.fetchall()
    for i in range(len(ids)):
        response.append(Get_details(request, 'Users', 'email', str(ids[i][0])))

    connection.close()
    return response


def Get_list(request, table, key, value):
    response = []
    params = dict(request.GET.iterlists())
    #optional parametrs
    date = params.get('since',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())
    #spesial for Thread_ListPosts
    sort = params.get('sort',('flat',))
    dateQuery = ''
    limitQuery = ''

    if (date):
        date = date[0].encode('utf8')
        dateQuery = 'AND date > {}'.format('%r'%date)
    if (limit):
        limit = limit[0]
        limitQuery = 'LIMIT {}'.format(int(limit)) #?

    order = order[0].encode('utf8')
    query = 'SELECT id FROM {0} WHERE {1}={2} {3} ORDER BY date {4} {5}'.format(table, key, '%r'%value, dateQuery, order, limitQuery)
    cursor = connection.cursor()
    cursor.execute(query)
    ids = cursor.fetchall()
    for i in range(len(ids)):
        response.append(Get_details(request, table, 'id', str(ids[i][0])))

    connection.close()
    return response

@csrf_exempt
def Get_details(request, table, fieldName, value, fields = ['all']):
    cursor = connection.cursor()
    subdict = {}

    if(fields.count('all')!= 0):
        query = 'SHOW COLUMNS FROM {}'.format(table)
        cursor.execute(query)
        columns = cursor.fetchall()
        keys = [columns[j][0] for j in range(len(columns))]
        if(table == 'Users'):
            queryStr = 'SELECT GROUP_CONCAT(followers), GROUP_CONCAT(following) FROM FollowingTable WHERE {0} = {1}'.format(fieldName, '%r'%value)
            cursor.execute(queryStr)
            followList = cursor.fetchone()
            subdict['followers'] = [] if (followList[0] is None) else followList[0].split(',')
            subdict['following'] = [] if (followList[1] is None) else followList[1].split(',')
            queryStr = 'SELECT GROUP_CONCAT(subscriptions) FROM SubscriptionsTable WHERE {0} = {1}'.format(fieldName, '%r'%value)
            cursor.execute(queryStr)
            subList = cursor.fetchone()
            idList = [] if (subList[0] is None) else subList[0].split(',')
            for i in range(len(idList)):
                idList[i] = int(idList[i])
            subdict['subscriptions'] = idList
    else:
        keys = fields

    fieldSting = ', '.join(keys)
    query = 'SELECT {0} FROM {1} WHERE {2} = {3}'.format(fieldSting, table, fieldName, '%r'%value)
    cursor.execute(query)
    data = cursor.fetchone()
    response = dict(izip(keys, data))
    response.update(subdict)
    if (response.has_key('date')):
        response['date'] = str(response['date'])
    return response

def Get_optional(request, possible, thisTable, thisKey, required):
    params = dict(request.GET.iterlists())
    dictionary = {}
    optional = params.get('related',())
    cursor = connection.cursor()
    for elem in optional:
        if(elem in possible.keys()):
            table = elem.capitalize()+'s'
            query = 'SELECT {0} FROM {1} WHERE {2}={3}'.format(elem, thisTable, thisKey, '%r'%required)
            cursor.execute(query)
            value = str(cursor.fetchone()[0])
            dictionary[elem] = Get_details(request, table, possible[elem], value.encode('utf8'))
    return dictionary

@csrf_exempt
def Create(request, table, keyField, fields):
    code = 0
    response = {}
    try:
        creation_info = json.loads(request.body)
        try:
            cursor = connection.cursor()
        except:
            code = 4
            response = 'Unknown Error'
        try:
            strings = []
            for value in creation_info.values():
                if(type(value) == bool):
                    value = 'true' if(value == True) else 'false'
                if(type(value) == int):
                    value = str(value)
                strings.append('%r'%value.encode('utf8'))
            query = 'INSERT INTO {0}({1}) VALUES({2})'.format(table, ', '.join(creation_info.keys()),', '.join(strings))
            cursor.execute(query)
            value = creation_info[keyField].encode('utf8')
            response = Get_details(request, table, keyField, value, fields)#only some fields
            if(table == 'Posts'):
                subquery = 'UPDATE Threads SET posts = posts+1 where id = {}'.format(int(response['thread']))
                cursor.execute(subquery)

        except IntegrityError:
            code = 5
            if(table == 'Users'):
                response = 'This user is already exists'
            else:
                value = creation_info[keyField].encode('utf8')
                response = Get_details(request, table, keyField, value, fields)#only some fields
        except (ProgrammingError, OperationalError):
            code = 3
            response = 'Synopsys Error'
    except ValueError:
        code = 2
        response = 'Validation Error'
    finally:
        connection.close()
    dictionary = {'code': code, 'response': response }
    return dictionary

def update(request, table, getkey, keyField):
    cursor = connection.cursor()
    params = json.loads(request.body)
    code = 0
    response = {}
    keyValue = params.pop(getkey)
    query = 'UPDATE {0} SET {1}=%s WHERE {2} = {3}'.format(table, '=%s, '.join(params.keys()),
             keyField, '%r'%str(keyValue).encode('utf8'))
    try:
        cursor.execute(query, params.values())
        response = Get_details(request, table, keyField, keyValue)#all fields
    except IntegrityError:
        code = 1
        response = 'User not found'
    except (ProgrammingError, OperationalError):
        code = 3
        response = 'Syntax Error'
    finally:
        connection.close()
    dictionary = {'code':code, 'response': response}
    return dictionary

def Vote(request, table, key):
    params = json.loads(request.body)
    code = 0
    key_id = params[key]
    cursor = connection.cursor()
    if(params['vote'] == 1):
        sub = 'likes = likes + 1'
        points = 'points = points+1'
    if(params['vote'] == -1):
        sub = 'dislikes = dislikes + 1'
        points = 'points = points-1'

    query = 'UPDATE {0} SET {1},{2} WHERE id = {3}'.format(table, sub, points, key_id)
    cursor.execute(query)
    response = Get_details(request, table, 'id', key_id)#all fields
    dictionary = {'code':code, 'response': response}
    return dictionary

#if this is thread, all it's posts isDeleted!
def DeleteOrNot(request, table, key, flag):
    cursor = connection.cursor()
    params = json.loads(request.body)
    code = 0
    sub = 'true' if(flag == True) else 'false'
    try:
        if(key == 'thread'):
            subquery = 'UPDATE Posts SET isDeleted = {0} where thread = {1}'.format(sub, params[key])
        if(key == 'post'):
            q1 = 'SELECT id FROM Threads WHERE post = {}'.format(params[key])
            cursor.execute(q1)
            thread_id = cursor.fetchone()[0]
            q2 = '-1' if(flag == True) else '+1'
            subquery = 'UPDATE Threads SET posts = posts{0} where id = {1}'.format(q2,int(thread_id))

        cursor.execute(subquery)
        query = 'UPDATE {0} SET isDeleted = {1} WHERE id = {2}'.format(table, sub, params[key])
        cursor.execute(query)
        response = params
    except IntegrityError:
        code = 1
        response = 'Object not found'
    dictionary = {'code' : code, 'response': response}
    return dictionary

def OpenOrClose(request, key, flag):
    cursor = connection.cursor()
    params = json.loads(request.body)
    code = 0
    try:
        query = 'UPDATE Threads SET isClosed = {0} WHERE id = {1}'.format(flag, params[key])
        cursor.execute(query)
        response = params
    except IntegrityError:
        code = 1
        response = 'Object not found'
    dictionary = {'code' : code, 'response': response}
    return dictionary

def subscribeOrNot(request, flag):
    cursor = connection.cursor()
    code = 0
    params = json.loads(request.body)
    email = '%r'%params['user'].encode('utf8')
    thread = params['thread']
    if(flag == True):
        query = 'INSERT INTO SubscriptionsTable(email, subscriptions) VALUES ({0},{1})'.format(email, thread)
    else:
        query = 'DELETE FROM SubscriptionsTable WHERE email={0} AND subscriptions={1}'.format(email, thread)
    try:
        cursor.execute(query)
        response = params
    except IntegrityError:
        code = 1
        response = 'Thread or user doesnt exist'
    finally:
        connection.close()

    dictionary = {'code': code, 'response': response}
    return dictionary

def followOrNot(request, flag):
    cursor = connection.cursor()
    code = 0
    params = json.loads(request.body)
    user = '%r'%params['follower'].encode('utf8') #our user is follower
    followee = '%r'%params['followee'].encode('utf8')
    if(flag == True):
        query1 = 'INSERT INTO FollowingTable(email, followers, following) VALUES ({0},{1},{2})'.format(user, followee, followee)
        query2 = 'INSERT INTO FollowingTable(email, followers, following) VALUES ({0},{1},{2})'.format(followee, user, user)
    else:
        query1 = 'DELETE FROM FollowingTable WHERE email = {} '.format(user)
        query2 = 'DELETE FROM FollowingTable WHERE email = {} '.format(followee)
    try:
        cursor.execute(query1)
        cursor.execute(query2)
        response = Get_details(request, 'Users', 'email', user)#all fields
    except IntegrityError:
        code = 1
        response = 'Follower or followee doesnt exist'
    finally:
        connection.close()
    dictionary = {'code': code, 'response': response}
    return dictionary
'''
