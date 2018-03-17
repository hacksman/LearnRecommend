# -*- coding: utf-8 -*-
# @Time    : 3/11/18 2:25 PM

from math import sqrt
from create_datas import Lips_data
from create_datas import Videos_data

def xzz_sim_distance(perfs, person1, person2):
    '''
    小祖宗相似度计算
     :return 一个0~1之间的值，越大表示两人相似度越高
    '''

    # 判断如果两人存在共同爱好,跳出来计算两人之间的差值总和
    # 判断如果两人不存在相同爱好,则返回0

    for per_person1_like in perfs[person1]:
        if per_person1_like in perfs[person2]:
            break
    else:
        return 0

    # 计算每一组差值的平方和
    sum_squares_sim = sum([pow(perfs[person2][per_saw] - perfs[person1][per_saw], 2) for per_saw in perfs[person1] if per_saw in perfs[person2]])

    # 避免因为两者完全相等时,分母为0；取导数时,则保证,数值越大,表明两者越相关,方便记忆。
    return 1/(1 + sqrt(sum_squares_sim))


def xzz_sim_person(perfs, p1, p2):
    '''
     小祖宗皮尔逊相关系数计算
    :return 一个0~1之间的值，越大表示两人相似度越高
    '''

    # 构建共同数据集
    common = {}
    for per_p1 in perfs[p1]:
        if per_p1 in perfs[p2]:
            common[per_p1] = 1

    # 得到数据集总数量
    n = len(common)

    # 没有共同兴趣爱好
    if n == 0:
        return 0

    # 对所有偏好求和
    sum1 = sum([perfs[p1][per_common] for per_common in common])
    sum2 = sum([perfs[p2][per_common] for per_common in common])

    # 求平方和
    sq_sum1 = sum([pow(perfs[p1][per_common], 2) for per_common in common])
    sq_sum2 = sum([pow(perfs[p2][per_common], 2) for per_common in common])

    # 求乘积和
    mul_sum = sum([perfs[p1][per_common] * perfs[p2][per_common] for per_common in common])

    num = mul_sum - sum1*sum2/n
    den = sqrt((sq_sum1 - pow(sum1, 2)/n)*(sq_sum2 - pow(sum2, 2)/n))

    if den == 0:
        return 0

    r = num/den
    return r


def xzz_top_matches(prefs, person, n=5, similarity=xzz_sim_person):
    '''
    小祖宗最n临近人算法
    寻找与自己最相近的n个人,并给出相似度评分
    '''
    scores = [(similarity(prefs, person, per_person), per_person) for per_person in prefs if per_person != person]

    scores.sort()
    scores.reverse()
    return scores[0:n]


def xzz_get_recommendations(perfs, person, similarity=xzz_sim_person):
    """
    小祖宗物品推荐算法
    基于相似度评分,进行加权计算,进行推荐建议
    """

    sim_rew_sum = {}
    sim_sum = {}

    for per_person in perfs:
        # 不与自己比较
        if per_person == person:
            continue

        similar = similarity(perfs, person, per_person)

        # 忽略总分小于0的情况
        if similar <= 0:
            continue

        for per_item in perfs[per_person]:

            # 只对自己没了解过的牌子进行评价
            if per_item not in perfs[person] or perfs[person][per_item] == 0:

                # 相似度*评价值之和
                sim_rew_sum.setdefault(per_item, 0)
                sim_rew_sum[per_item] += perfs[per_person][per_item] * similar

                # 相似度之和
                sim_sum.setdefault(per_item, 0)
                sim_sum[per_item] += similar

    ranks = [(sim_rew_sum[item]/sim_sum[item], item) for item in sim_rew_sum]
    ranks.sort()
    ranks.reverse()
    return ranks


def xzz_transform_prefs(prefs):
    '''
    转置字典操作,可以理解为矩阵转置操作
    '''
    result = {}
    for per_person in prefs:
        for per_item in prefs[per_person]:
            result.setdefault(per_item, {})
            result[per_item][per_person] = prefs[per_person][per_item]

    return result


def xzz_calcilate_similar_items(prefs, n=10):
    """
    item-based collaborative filtering
     基于物品的协作性过滤
     :return : 给出与这些物品最相近的n个其他物品
    """
    result = {}
    item_prefs = transform_prefs(prefs)

    c = 0
    for per_item in item_prefs:
        c += 1
        if c % 100 == 0:
            print "%d / %d" % (c, len(item_prefs))
        scores = top_matches(item_prefs, per_item, n=n, similarity=sim_distance)
        result[per_item] = scores
    return result


def xzz_get_recommend_item(prefs, item_match, user):
    """
     根据物品相似度评分,作为权重进行加权计算,来得到未看过影片的评分
    """
    user_ratings = prefs[user]
    scores = {}
    total_sim = {}

    for (item1, rating) in user_ratings.items():

        for (similarity, item2) in item_match[item1]:

            # 跳过对已经评分的作品
            if item2 in user_ratings:
                continue

            scores.setdefault(item2, 0)
            scores[item2] += similarity*rating

            total_sim.setdefault(item2, 0)
            total_sim[item2] += similarity

    result = [(scores[item]/total_sim[item], item) for item in scores]
    result.sort()
    result.reverse()
    return result


if __name__ == '__main__':
    # for per_p in Videos_data:
    #     # 不与自己进行比较
    #     if per_p == 'per_0':
    #         continue
    #     print xzz_sim_person(Videos_data, 'per_0', per_p), per_p
    print xzz_top_matches(Videos_data, 'per_0', n=5, similarity=xzz_sim_person)


