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

db = MySQLdb.connect("localhost","root","f66n9zae2f","API",charset='utf8', init_command='SET NAMES UTF8')
db.set_character_set('utf8')
dbc = db.cursor()
dbc.execute('SET Names utf8;')
dbc.execute('set character set utf8;')
dbc.execute('set character_set_connection=utf8;')
dbc.execute("SET SESSION collation_connection = 'utf8_general_ci';")
db.commit()


def set_quots(data):
    if data is None:
        return '%s' % 'Null'
    result = "'" + '%s' % data + "'"
    if not ((type(data) == str) or (type(data) == unicode)):
        result = '%s' % data
    return result

def check_none(data):
    if (data == 'Null'):
        return None


@csrf_exempt
def clear(request):
    cursor = db.cursor()
    cursor.execute('SET FOREIGN_KEY_CHECKS = 0;');
    cursor.execute('TRUNCATE Post')
    cursor.execute('TRUNCATE Subscriptions')
    cursor.execute('TRUNCATE Thread')
    cursor.execute('TRUNCATE Forum')
    cursor.execute('TRUNCATE Follow')
    cursor.execute('TRUNCATE User')
    db.commit()
    dictionary = {'code' : 0, 'response': 'OK'}
    return JsonResponse(dictionary)

@csrf_exempt
def status(request):
    response = {}
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM User')
    response['user'] = int(cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM Thread where isDeleted = false')
    response['thread'] = int(cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM Forum')
    response['forum'] = int(cursor.fetchone()[0])
    cursor.execute('SELECT COUNT(*) FROM Post where isDeleted = false')
    response['post'] = int(cursor.fetchone()[0])
    dictionary = {'code': 0, 'response': response}
    return JsonResponse(dictionary)


@csrf_exempt
def create(request):
    code = 0
    url = request.path
    table = url.replace('/db/api/','').replace('/create','').replace('/','').capitalize()
    params = json.loads(request.body)
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
    try:
        cursor.execute(query)
        db.commit()
        key = 'id' + table;
        value = cursor.lastrowid

        if(table == 'Post'):
            idThread = params['thread']
            subquery = 'UPDATE Thread SET posts = posts+1 where idThread = ' + set_quots(idThread) + ';'
            cursor.execute(subquery)
            db.commit()

        response = params
        response.update({'id' : value})
    except:
        code =  5
        response = 'Error type 5'

    dictionary = {'code' : code, 'response' : response}
    return JsonResponse(dictionary)


@csrf_exempt
def details(request):
    url = request.path
    table = url.replace('/db/api/','').replace('/details','').replace('/','')
    params = dict(request.GET.iterlists())
    required = params.get(table,())
    keys = {'user' : 'email', 'forum' : 'short_name', 'thread' : 'idThread', 'post' : 'idPost'}
    key = keys.get(table,'')
    table = table.capitalize()
    value = set_quots(required[0])
    response = get_details(table, key, value)
    if response is None:
        dictionary = {'code' : 1, 'response' : 'Error type 1'}
        return JsonResponse(dictionary)

    possible = {'Forum' : ['user'], 'Thread' : ['user', 'forum'], 'Post' : ['user', 'forum', 'thread']}
    sub_dict = {}
    optional = params.get('related',())
    cursor = db.cursor()
    for elem in optional:
        if(elem in possible[table]):
            value = set_quots(response[elem])
            sub_dict[elem] = get_details(elem.capitalize(), keys[elem] , value)
        else:
            dictionary = {'code' : 3, 'response' : 'Error type 3'}
            return JsonResponse(dictionary)

    response.update(sub_dict)
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def listUsersf(request):
    params = dict(request.GET.iterlists())
    required = params.get('forum',())
    since_id = params.get('since_id',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())

    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = 'AND p.user >= {}'.format(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY u.name {}'.format(order)
    full_opt_query = since_query + order_query + limit_query
    sub_query = 'p.forum IN (SELECT idForum FROM Forum WHERE short_name = ' + set_quots(required[0]) + ')'
    query = 'SELECT DISTINCT user FROM Post p, User u WHERE p.user = u.idUser AND ' + sub_query + full_opt_query +';'
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idUser = set_quots(cursor.fetchone()[0])
        response.append(get_details('User', 'idUser', idUser))

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)



@csrf_exempt
def listThreadsf(request):
    params = dict(request.GET.iterlists())
    required = params.get('forum',())
    since_id = params.get('since',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())
    optional = params.get('related',())

    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = 'AND date >= ' + set_quots(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY date {}'.format(order)
    full_opt_query = since_query + order_query + limit_query
    sub_query = ' forum IN (SELECT idForum FROM Forum WHERE short_name = ' + set_quots(required[0]) + ')'
    query = 'SELECT DISTINCT idThread FROM Thread WHERE' + sub_query + full_opt_query +';'

    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idThread = set_quots(cursor.fetchone()[0])
        sub_dict = {}
        sub_dict = get_details('Thread', 'idThread', idThread)
        if ('user' in optional):
            usr_email = sub_dict['user']
            sub_dict['user'] = get_details('User', 'email', set_quots(usr_email))
        if ('forum' in optional):
            frm_shortname = sub_dict['forum']
            sub_dict['forum'] = get_details('Forum', 'short_name', set_quots(frm_shortname))
        response.append(sub_dict)

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)


@csrf_exempt
def listPostsf(request):
    params = dict(request.GET.iterlists())
    required = params.get('forum',())
    since_id = params.get('since',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())
    optional = params.get('related',())

    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = 'AND date >= ' + set_quots(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY date {}'.format(order)
    full_opt_query = since_query + order_query + limit_query
    sub_query = ' forum IN (SELECT idForum FROM Forum WHERE short_name = ' + set_quots(required[0]) + ')'
    query = 'SELECT DISTINCT idPost FROM Post WHERE' + sub_query + full_opt_query +';'

    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idPost = set_quots(cursor.fetchone()[0])
        sub_dict = {}
        sub_dict = get_details('Post', 'idPost', idPost)
        if ('user' in optional):
            usr_email = sub_dict['user']
            sub_dict['user'] = get_details('User', 'email', set_quots(usr_email))
        if ('forum' in optional):
            frm_shortname = sub_dict['forum']
            sub_dict['forum'] = get_details('Forum', 'short_name', set_quots(frm_shortname))
        if('thread' in optional):
            idThread = sub_dict['thread']
            sub_dict['thread'] = get_details('Thread', 'idThread', set_quots(idThread))
        response.append(sub_dict)

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def listp(request):
    params = dict(request.GET.iterlists())
    required = params.get('forum',()) or params.get('thread', ())  #thread OR forum
    sub_query = ''
    if ('forum' in params.keys()):
        sub_query = ' forum IN (SELECT idForum FROM Forum WHERE short_name = ' + set_quots(required[0]) + ')'
    if('thread' in params.keys()):
        sub_query = 'thread = {}'.format(required[0])

    since_id = params.get('since',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())
    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = ' AND date >= ' + set_quots(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY date {}'.format(order)
    full_opt_query = since_query + order_query + limit_query
    query = 'SELECT DISTINCT idPost FROM Post WHERE ' + sub_query + full_opt_query +';'

    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idPost = set_quots(cursor.fetchone()[0])
        response.append(get_details('Post', 'idPost', idPost))

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def removep(request):
    params = json.loads(request.body)
    idPost = params.get('post', ())

    cursor = db.cursor()
    query = 'UPDATE Post SET isDeleted = true WHERE idPost = ' + set_quots(idPost)
    cursor.execute(query)
    query = 'UPDATE Thread SET posts = posts-1 WHERE idThread IN (SELECT thread from Post WHERE idPost = ' + set_quots(idPost) + ');'
    cursor.execute(query)
    db.commit()

    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)

@csrf_exempt
def restorep(request):
    params = json.loads(request.body)
    idPost = params.get('post', ())
    cursor = db.cursor()
    query = 'UPDATE Post SET isDeleted = false WHERE idPost = ' + set_quots(idPost)
    cursor.execute(query)
    query = 'UPDATE Thread SET posts = posts+1 WHERE idThread IN (SELECT thread from Post WHERE idPost = ' + set_quots(idPost) + ');'
    cursor.execute(query)
    db.commit()

    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)

@csrf_exempt
def votep(request):
    params = json.loads(request.body)
    idPost = params.get('post', ())

    vote = params.get('vote', ())
    if (vote == 1):
        word = 'likes'
        inc = ' + 1'
    if (vote == -1):
        word = 'dislikes'
        inc = ' - 1'

    cursor = db.cursor()
    query = 'UPDATE Post set {0} = {0} + 1 WHERE idPost = '.format(word)
    query = query + set_quots(idPost)
    cursor.execute(query)

    query = 'UPDATE Post SET points = points' + inc
    query = query + ' WHERE idPost = ' + set_quots(idPost)
    cursor.execute(query)
    db.commit()

    response = get_details('Post', 'idPost', set_quots(idPost))
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)


@csrf_exempt
def update(request):
    params = json.loads(request.body)
    idPost = params.get('post', ())
    message = params.get('message',())

    cursor = db.cursor()
    query = 'UPDATE Post SET message = ' + set_quots(message) + ' WHERE idPost = ' + set_quots(idPost)
    cursor.execute(query)
    db.commit()
    response = get_details('Post', 'idPost', set_quots(idPost))
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def follow(request):
    params = json.loads(request.body)
    follower = params.get('follower', ())
    followee = params.get('followee',())
    cursor = db.cursor()
    user_query = 'SELECT idUser FROM User WHERE email = ' + set_quots(follower)
    cursor.execute(user_query)
    db.commit()
    idU = cursor.fetchone()[0]

    followee_query = 'SELECT idUser FROM User WHERE email = ' + set_quots(followee)
    cursor.execute(followee_query)
    db.commit()
    idF = cursor.fetchone()[0]

    query = 'INSERT INTO Follow(user, followee) VALUES ({0}, {1})'.format(set_quots(idU), set_quots(idF))
    cursor.execute(query)
    query = 'INSERT INTO Follow(user, follower) VALUES ({1}, {0})'.format(set_quots(idU), set_quots(idF))
    cursor.execute(query)
    db.commit()

    response = get_details('User', 'idUser', set_quots(idU))
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def unfollow(request):
    params = json.loads(request.body)
    follower = params.get('follower', ())
    followee = params.get('followee',())
    cursor = db.cursor()
    user_query = 'SELECT idUser FROM User WHERE email = ' + set_quots(follower)
    cursor.execute(user_query)
    db.commit()
    idU = cursor.fetchone()[0]

    followee_query = 'SELECT idUser FROM User WHERE email = ' + set_quots(followee)
    cursor.execute(followee_query)
    db.commit()
    idF = cursor.fetchone()[0]

    query = 'DELETE FROM Follow WHERE user = ' + set_quots(idU) + ' AND followee = ' + set_quots(idF)
    cursor.execute(query)
    query = 'DELETE FROM Follow WHERE user = ' + set_quots(idF) + ' AND follower = ' + set_quots(idU)
    cursor.execute(query)
    db.commit()

    response = get_details('User', 'idUser', set_quots(idU))
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def updateu(request):
    params = json.loads(request.body)
    about = params.get('about', ())
    name = params.get('name',())
    email = params.get('user', ())

    cursor = db.cursor()
    query = 'UPDATE User SET about = ' + set_quots(about) + ' , name = ' + set_quots(name)
    query = query + ' WHERE email = ' + set_quots(email)
    cursor.execute(query)
    db.commit()
    response = get_details('User', 'email', set_quots(email))
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def listfollowers(request):
    params = dict(request.GET.iterlists())
    user = params.get('user',())
    since_id = params.get('since_id',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())

    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = 'AND f.user >= {}'.format(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY u.name {}'.format(order)

    cursor = db.cursor()
    query = 'SELECT f.user FROM Follow f, User u WHERE f.user = u.idUser AND followee IN '
    query = query + ' (SELECT idUser FROM User WHERE email = ' + set_quots(user[0]) + ') '
    query = query + since_query + order_query + limit_query

    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idUser = set_quots(cursor.fetchone()[0])
        response.append(get_details('User', 'idUser', idUser))

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def listfollowing(request):
    params = dict(request.GET.iterlists())
    user = params.get('user',())
    since_id = params.get('since_id',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())

    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = 'AND f.user >= {}'.format(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY u.name {}'.format(order)

    cursor = db.cursor()
    query = 'SELECT f.user FROM Follow f, User u WHERE f.user = u.idUser AND follower IN '
    query = query + ' (SELECT idUser FROM User WHERE email = ' + set_quots(user[0]) + ') '
    query = query + since_query + order_query + limit_query

    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idUser = set_quots(cursor.fetchone()[0])
        response.append(get_details('User', 'idUser', idUser))

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def listpostsu(request):
    params = dict(request.GET.iterlists())
    required = params.get('user',())
    since_id = params.get('since',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())

    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = 'AND date >= ' + set_quots(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY date {}'.format(order)
    full_opt_query = since_query + order_query + limit_query
    sub_query = ' user IN (SELECT idUser FROM User WHERE email = ' + set_quots(required[0]) + ')'
    query = 'SELECT DISTINCT idPost FROM Post WHERE' + sub_query + full_opt_query +';'

    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idPost = set_quots(cursor.fetchone()[0])
        response.append(get_details('Post', 'idPost', idPost))

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def closet(request):
    params = json.loads(request.body)
    idThread = params.get('thread', ())
    cursor = db.cursor()
    query = 'UPDATE Thread SET isClosed = true WHERE idThread = ' + set_quots(idThread) +';'
    cursor.execute(query)
    db.commit()
    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)

@csrf_exempt
def opent(request):
    params = json.loads(request.body)
    idThread = params.get('thread', ())
    cursor = db.cursor()
    query = 'UPDATE Thread SET isClosed = false WHERE idThread = ' + set_quots(idThread) +';'
    cursor.execute(query)
    db.commit()
    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)

@csrf_exempt
def removet(request):
    params = json.loads(request.body)
    idThread = params.get('thread', ())
    cursor = db.cursor()
    query = 'UPDATE Thread SET isDeleted = true, posts = 0 WHERE idThread = ' + set_quots(idThread) +';'
    cursor.execute(query)
    query = 'UPDATE Post SET isDeleted = true WHERE thread = ' + set_quots(idThread) + ';'
    cursor.execute(query)
    db.commit()
    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)

@csrf_exempt
def restoret(request):
    params = json.loads(request.body)
    idThread = params.get('thread', ())
    cursor = db.cursor()
    query = 'UPDATE Post SET isDeleted = false WHERE thread = ' + set_quots(idThread) + ';'
    cursor.execute(query)
    posts = cursor.rowcount
    query = 'UPDATE Thread SET isDeleted = false, posts = ' + set_quots(posts) +' WHERE idThread = ' + set_quots(idThread) +';'
    cursor.execute(query)
    db.commit()
    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)

@csrf_exempt
def votet(request):
    params = json.loads(request.body)
    idThread = params.get('thread', ())

    vote = params.get('vote', ())
    if (vote == 1):
        word = 'likes'
        inc = ' + 1'
    if (vote == -1):
        word = 'dislikes'
        inc = ' - 1'

    cursor = db.cursor()
    query = 'UPDATE Thread set {0} = {0} + 1 WHERE idThread = '.format(word)
    query = query + set_quots(idThread)
    cursor.execute(query)

    query = 'UPDATE Thread SET points = points' + inc
    query = query + ' WHERE idThread = ' + set_quots(idThread)
    cursor.execute(query)
    db.commit()

    response = get_details('Thread', 'idThread', set_quots(idThread))
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def updatet(request):
    params = json.loads(request.body)
    message = params.get('message', ())
    slug = params.get('slug',())
    idThread = params.get('thread', ())

    cursor = db.cursor()
    query = 'UPDATE Thread SET message = ' + set_quots(message) + ' , slug = ' + set_quots(slug)
    query = query + ' WHERE idThread = ' + set_quots(idThread)
    cursor.execute(query)
    db.commit()
    response = get_details('Thread', 'idThread', set_quots(idThread))
    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)

@csrf_exempt
def subscribe(request):
    params = json.loads(request.body)
    user = params.get('user', ())
    thread = params.get('thread',())
    cursor = db.cursor()
    user_query = 'SELECT idUser FROM User WHERE email = ' + set_quots(user)
    cursor.execute(user_query)
    db.commit()
    idU = cursor.fetchone()[0]
    query = 'INSERT INTO Subscriptions(user, subscription) VALUES ({0}, {1})'.format(set_quots(idU), set_quots(thread))
    cursor.execute(query)
    db.commit()

    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)


@csrf_exempt
def unsubscribe(request):
    params = json.loads(request.body)
    user = params.get('user', ())
    thread = params.get('thread',())
    cursor = db.cursor()
    user_query = 'SELECT idUser FROM User WHERE email = ' + set_quots(user)
    cursor.execute(user_query)
    db.commit()
    idU = cursor.fetchone()[0]
    query = 'DELETE FROM Subscriptions WHERE user = {0} AND subscription = {1}'.format(set_quots(idU), set_quots(thread))
    cursor.execute(query)
    db.commit()

    dictionary = {'code' : 0, 'response' : params}
    return JsonResponse(dictionary)

@csrf_exempt
def listt(request):
    params = dict(request.GET.iterlists())
    required = params.get('forum',()) or params.get('user', ())
    sub_query = ''
    if ('forum' in params.keys()):
        sub_query = ' forum IN (SELECT idForum FROM Forum WHERE short_name = ' + set_quots(required[0]) + ')'
    if('user' in params.keys()):
        sub_query = ' user IN (SELECT idUser FROM User WHERE email = ' + set_quots(required[0]) + ')'

    since_id = params.get('since',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())
    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = ' AND date >= ' + set_quots(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY date {}'.format(order)
    full_opt_query = since_query + order_query + limit_query
    query = 'SELECT DISTINCT idThread FROM Thread WHERE ' + sub_query + full_opt_query +';'

    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    response = []
    for i in xrange(cursor.rowcount):
        idThread = set_quots(cursor.fetchone()[0])
        response.append(get_details('Thread', 'idThread', idThread))

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)


@csrf_exempt
def listPostst(request):
    params = dict(request.GET.iterlists())
    response = []
    required = params.get('thread',())
    since_id = params.get('since',())
    order = params.get('order',('desc',))
    limit = params.get('limit',())

    sort = params.get('sort',('flat',))  #
    sort = sort[0] #

    since_query = ''
    limit_query = ''
    if(since_id):
        since_id = since_id[0]
        since_query = ' AND date >= ' + set_quots(since_id)
    if(limit):
        limit = limit[0]
        limit_query = ' LIMIT {}'.format(limit)
    order = order[0]
    order_query = ' ORDER BY date {}'.format(order)
    sub_query = ' thread = {}'.format(required[0])
    cursor = db.cursor()

    if(sort == 'flat'):
        full_opt_query = since_query + order_query + limit_query
        query = 'SELECT idPost FROM Post WHERE' + sub_query + full_opt_query +';'

        cursor.execute(query)
        db.commit()
        for i in xrange(cursor.rowcount):
            idPost = set_quots(cursor.fetchone()[0])
            response.append(get_details('Post', 'idPost', idPost))

    if(sort == 'tree'):
        full_opt_query = since_query + ' AND parent IS NULL' + order_query
        query = 'SELECT idPost FROM Post WHERE' + sub_query + full_opt_query +';'
        cursor.execute(query)
        db.commit()
        for row in cursor.fetchall():
            idPost = row[0]
            tree_sort(idPost, required[0], int(limit), response)

    if(sort == 'parent_tree'):
        full_opt_query = since_query + ' AND parent IS NULL' + order_query + limit_query
        query = 'SELECT idPost FROM Post WHERE' + sub_query + full_opt_query +';'
        cursor.execute(query)
        db.commit()
        for row in cursor.fetchall():
            idPost = row[0]
            parent_tree_sort(idPost, required[0], response)

    dictionary = {'code' : 0, 'response' : response}
    return JsonResponse(dictionary)


def tree_sort(idPost, idThread, limit, response):
    if len(response) == limit:
        return
    response.append(get_details('Post', 'idPost', set_quots(idPost)))
    query = 'SELECT idPost from Post WHERE thread = ' + set_quots(idThread) + ' AND parent = ' + set_quots(idPost) + ';'
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    for row in cursor.fetchall():
        child = row[0]
        tree_sort(child, idThread, limit, response)



def parent_tree_sort(idPost, idThread, response):
    tree_sort(idPost, idThread, 'unlimited' , response)


def get_details(table, key, value):
    response = {}
    query = 'SHOW COLUMNS FROM {}'.format(table)
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()
    columns = cursor.fetchall()
    keys = [columns[j][0] for j in range(len(columns))]
    query = 'SELECT {0} FROM {1} WHERE {2} = '.format(', '.join(keys), table, key) + value + ';'
    cursor.execute(query)
    db.commit()

    data = cursor.fetchone()
    if data is None:
        return None

    response = dict(izip(keys, data))
    if (response.has_key('date')):
        response['date'] = str(response['date'])

    id_val = response.pop('id'+table)
    response['id'] = id_val
    id_val = set_quots(id_val)

    subdict = {}
    if(table == 'User'):
        subdict = optional_user_fields(id_val)
    else:
        idUser = set_quots(response['user'])
        query = 'SELECT email FROM User WHERE idUser = ' + idUser + ';'
        cursor.execute(query)
        db.commit()
        user_email = cursor.fetchone()[0]
        subdict['user'] = user_email

        if 'forum' in response.keys():
            idForum = set_quots(response['forum'])
            query = 'SELECT short_name FROM Forum WHERE idForum = ' + idForum + ';'
            cursor.execute(query)
            db.commit()
            forum_shortname = cursor.fetchone()[0]
            subdict['forum'] = forum_shortname

    response.update(subdict)
    return response


def optional_user_fields(id):
    subdict = {}
    cursor = db.cursor()
    subquery = '(SELECT follower FROM Follow WHERE user = {})'.format(id)
    query = 'SELECT email FROM User WHERE idUser in {0}'.format(subquery)
    cursor.execute(query)
    db.commit()
    emails = []
    for i in xrange(cursor.rowcount):
        emails.append(cursor.fetchone()[0])
    subdict['followers'] = emails

    subquery = '(SELECT followee FROM Follow WHERE user = {})'.format(id)
    query = 'SELECT email FROM User WHERE idUser in {0}'.format(subquery)
    cursor.execute(query)
    db.commit()
    emails = []
    for i in xrange(cursor.rowcount):
        emails.append(cursor.fetchone()[0])
    subdict['following'] = emails

    query = 'SELECT subscription FROM Subscriptions WHERE user = {}'.format(id)
    cursor.execute(query)
    db.commit()
    threads = []
    for i in xrange(cursor.rowcount):
        threads.append(cursor.fetchone()[0])
    subdict['subscriptions'] = threads
    return subdict
