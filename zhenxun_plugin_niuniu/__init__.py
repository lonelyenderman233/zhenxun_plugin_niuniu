from nonebot import on_command
from nonebot.params import CommandArg
from utils.utils import is_number
from utils.message_builder import image
from utils.image_utils import text2image
from nonebot.adapters.onebot.v11 import (
  GroupMessageEvent,
  Message)
from .data_source import *
from decimal import Decimal as de
import os
import time
import random

__zx_plugin_name__ = "牛牛大作战"
__plugin_usage__ = """
usage：
    牛牛大作战，男同快乐游。合理安排时间，享受健康生活
    【注册牛子】 --注册你的牛子
    【jj [@user]】 --与注册牛子的人击剑，奖励长度为双方绝对值总和的5%-15%，小牛子反杀奖励翻倍
    【我的牛子】 --查看自己牛子长度
    【牛子长度排行】 --查看本群正数牛子长度排行
    【牛子深度排行】 --查看本群负数牛子深度排行
    【打胶】 --对自己的牛子进行操作，结果随机
    牛子长度<-100进化成魅魔，与正牛子击剑有20%概率将对方吞噬（对牛头人只有10%概率触发），自身长度不变
    长度>100进化成牛头人，击剑有10%概率将对方归0，自身长度不变，对魅魔只有5%触发，对牛头人无效
    
""".strip()
__plugin_des__ = "牛子大作战(误"
__plugin_type__ = ("群内小游戏",)
__plugin_cmd__ = ["注册牛子", "jj/JJ/Jj/jJ", "我的牛子", "牛子长度排行","牛子深度排行", "打胶", "牛牛大作战"]
__plugin_version__ = 0.4
__plugin_author__ = "molanp"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ['注册牛子', 'jj', 'JJ', 'Jj', 'jJ', '我的牛子', '牛子长度排行','牛子深度排行', '打胶', '牛牛大作战'],
}

niuzi_register = on_command("注册牛子", priority=5, block=True)
niuzi_fencing = on_command("jj", aliases={'JJ', 'Jj', 'jJ'}, priority=5, block=True)
niuzi_my = on_command("我的牛子", priority=5, block=True)
niuzi_ranking = on_command("牛子长度排行", priority=5, block=True)
niuzi_ranking_e = on_command("牛子深度排行", priority=5, block=True)
niuzi_hit_glue = on_command("打胶", priority=5, block=True)

group_user_jj = {}
group_hit_glue = {}

path = os.path.dirname(__file__)

if not os.path.exists(f"{path}/data"):
    os.makedirs(f"{path}/data")
    with open(os.path.join(path, "data/long.json"), "w", encoding="utf-8") as f:
      f.write('{}')

@niuzi_register.handle()
async def _(event: GroupMessageEvent):
    group = str(event.group_id)
    qq = str(event.user_id)
    content = readInfo("data/long.json")
    long = random_long()
    try:
        pass
    except KeyError:
      content[group] = {}
    try:
      if content[group][qq]:
        await niuzi_register.finish(Message("你已经注册过牛子啦！"), at_sender=True)
    except KeyError:
      content[group][qq] = long
      readInfo('data/long.json', content)
      await niuzi_register.finish(Message(f"注册牛子成功，当前长度{long}cm"), at_sender=True)

@niuzi_fencing.handle()
async def _(event: GroupMessageEvent):
    qq = str(event.user_id)
    group = str(event.group_id)
    global group_user_jj
    try:
        pass
    except KeyError:
      group_user_jj[group] = {}
    try:
        pass
    except KeyError:
      group_user_jj[group][qq] = {}
    try:
        time_pass = int(time.time() - group_user_jj[group][qq]['time'])
        if time_pass < 3600*23:
            time_rest = 3600*23 - time_pass
            jj_refuse = [
                f'才过去了{time_pass // 3600}h,你就又要击剑了，真是饥渴难耐啊，{int(time_rest / 3600) + 1}h后再来吧',
                f'不行不行，你的身体会受不了的，歇{int(time_rest / 3600) + 1}h再来吧',
                f'你这种男同就应该被送去集中营！等待{int(time_rest / 3600) + 1}h再来吧',
                f'打咩哟！你的牛牛会炸的，休息{int(time_rest / 3600) + 1}h再来吧',
            ]
            await niuzi_fencing.finish(random.choice(jj_refuse), at_sender=True)
    except KeyError:
      pass
    #
    msg = event.get_message()
    content = readInfo("data/long.json")
    at_list = [msg_seg.data["qq"] for msg_seg in msg if msg_seg.type == "at"]
    try:
        my_long = de(str(content[group][qq]))
        if at_list:
            at = str(at_list[0])
            if len(at_list) >= 2:
              result = random.choice([
                "一战多？你的小身板扛得住吗？",
                "你不准参加Impart┗|｀O′|┛"
                ])
            elif at != qq:
              try:
                opponent_long = de(str(content[group][at]))
                group_user_jj[group][qq]['time'] = time.time()
                result = fencing(my_long, opponent_long, at, qq, group, content)
              except KeyError:
                result = "对方还没有牛子呢，你不能和ta击剑！请让对方发送 注册牛子"
            else:
              result = "不能和自己击剑哦！"
        else:
            result = "你要和谁击剑？你自己吗？"
    except KeyError:
      del group_user_jj[group][qq]['time']
      result = "你还没有牛子呢！不能击剑！请发送 注册牛子"
    finally:
        await niuzi_fencing.finish(Message(result),at_sender=True)

@niuzi_my.handle()
async def _(event: GroupMessageEvent):
    qq = str(event.user_id)
    group = str(event.group_id)
    content = readInfo("data/long.json")
    try:
        my_long = content[group][qq]
        if my_long <= -100:
            result = f"wtf？你已经进化成魅魔了！当前深度{format(my_long,'.2f')}cm"
            picc = """
      魅魔（稀有）：
          与正牛子击剑时有20%的几率触发吞噬，对方牛子归0（对牛头人只有10%概率触发）
      """
        elif -100 < my_long <= -50:
          result = f"嗯....好像已经穿过了身体吧..从另一面来看也可以算是凸出来的吧?当前深度{format(my_long,'.2f')}cm"
        elif -50 < my_long <= -25:
          result = random.choice([
            f"这名女生，你的身体很健康哦！当前深度{format(my_long,'.2f')}cm",
            f"WOW,真的凹进去了好多呢！当前深度{format(my_long,'.2f')}cm",
            f"你已经是我们女孩子的一员啦！当前深度{format(my_long,'.2f')}cm"
          ])
        elif -25 < my_long <= -10:
          result = random.choice([
            f"你已经是一名女生了呢，当前深度{format(my_long,'.2f')}cm",
            f"从女生的角度来说，你发育良好,当前深度{format(my_long,'.2f')}cm",
            f"你醒啦？你已经是一名女孩子啦！深度足足有{format(my_long,'.2f')}cm呢！",
            f"唔....可以放进去一根手指了都....当前深度{format(my_long,'.2f')}cm"
          ])
        elif -10 < my_long <= 0:
          result = random.choice([
            f"安了安了，不要伤心嘛，做女生有什么不好的啊。当前深度{format(my_long,'.2f')}cm",
            f"不哭不哭，摸摸头，虽然很难再长出来，但是请不要伤心啦啊！当前深度{format(my_long,'.2f')}cm",
            f"加油加油！我看好你哦！当前深度{format(my_long,'.2f')}cm",
            f"你醒啦？你现在已经是一名女孩子啦！当前深度{format(my_long,'.2f')}cm"
          ])
        elif 0 < my_long <= 10:
          result = random.choice([
            f"你行不行啊？细狗！牛子长度才{format(my_long,'.2f')}cm！",
            f"虽然短，但是小小的也很可爱呢。当前长度{format(my_long,'.2f')}cm",
            f"像一只蚕宝宝,当前牛子长度{format(my_long,'.2f')}cm！！！"
          ])
        elif 10 < my_long <= 25:
          result = random.choice([
            f"唔，当前牛子长度是{format(my_long,'.2f')}cm",
            f"已经很长呢！当前长度{format(my_long,'.2f')}cm"
          ])
        elif 25 < my_long <= 50:
          result = random.choice([
            f"话说这种真的有可能吗？当前牛子长度{format(my_long,'.2f')}cm",
            f"厚礼谢，你的牛子长度居然有{format(my_long,'.2f')}cm呢！！！"
          ])
        elif 50 < my_long <= 100:
          result = random.choice([
            f"已经突破天际了嘛...当前牛子长度{format(my_long,'.2f')}cm",
            f"唔...这玩意应该不会变得比我高吧？当前牛子长度{format(my_long,'.2f')}cm",
            f"你这个长度会死人的...当前牛子长度{format(my_long,'.2f')}cm！",
            f"你马上要进化成牛头人了！当前牛子长度{format(my_long,'.2f')}cm！",
            f"你是什么怪物，不要过来啊！当前牛子长度{format(my_long,'.2f')}cm！"
          ])
        else:
            result = f"惊世骇俗！你已经进化成牛头人了！当前牛子长度{format(my_long,'.2f')}cm！！！"
            picc = """
      牛头人：
          与所有牛子击剑时有10%的几率触发蛮牛冲撞，将对方牛子归0（对魅魔只有5%概率触发，对牛头人无效）
      """
    except KeyError:
      result = "你还没有牛子呢！"
    finally:
        try:
          await niuzi_my.send(image(b64=(await text2image(picc, color="#f9f6f2", padding=10)).pic2bs4()))
        except NameError:
          pass
        await niuzi_my.finish(Message(result),at_sender=True)

@niuzi_ranking.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    num = int(num) if is_number(num) and 51 > int(num) > 10 else 10
    all_users = get_all_users(str(event.group_id))
    all_user_id = []
    all_user_data = []
    for user_id, user_data in all_users.items():
      if user_data > 0:
        all_user_id.append(int(user_id))
        all_user_data.append(user_data)

    if all_user_id: 
        rank_image = await init_rank("牛子长度排行榜-单位cm", all_user_id, all_user_data, event.group_id, num)
        if rank_image:
            await niuzi_ranking.finish(image(b64=rank_image.pic2bs4()))
    else: 
        await niuzi_ranking.finish(Message("暂无此排行榜数据...", at_sender=True))
        
@niuzi_ranking_e.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    num = int(num) if is_number(num) and 51 > int(num) > 10 else 10
    all_users = get_all_users(str(event.group_id))
    all_user_id = []
    all_user_data = []
    for user_id, user_data in all_users.items():
      if user_data < 0:
        all_user_id.append(int(user_id))
        all_user_data.append(float(str(user_data)[1:]))

    if all_user_id: 
        rank_image = await init_rank("牛子深度排行榜-单位cm", all_user_id, all_user_data, event.group_id, num)
        if rank_image:
            await niuzi_ranking_e.finish(image(b64=rank_image.pic2bs4()))
    else: 
        await niuzi_ranking_e.finish(Message("暂无此排行榜数据..."), at_sender=True)


@niuzi_hit_glue.handle()
async def _(event: GroupMessageEvent):
    qq = str(event.user_id)
    group = str(event.group_id)
    global group_hit_glue
    try:
        pass
    except KeyError:
      group_hit_glue[group] = {}
    try:
        pass
    except KeyError:
      group_hit_glue[group][qq] = {}
    try:
        time_pass = int(time.time() - group_hit_glue[group][qq]['time'])
        if time_pass < 3600*23:
            time_rest = 3600*23 - time_pass
            glue_refuse = [
                f'才过去了{time_pass // 3600}h,你就又要打胶了，牛牛受得住吗？{int(time_rest / 3600) + 1}h后再来吧',
                f'不行不行，你的身体会受不了的，歇{int(time_rest / 3600) + 1}h再来吧',
                f'休息一下吧，会炸膛的！{int(time_rest / 3600) + 1}h后再来吧',
                f'打咩哟，你的牛牛会爆炸的，休息{int(time_rest / 3600) + 1}h再来吧',
            ]
            await niuzi_hit_glue.finish(random.choice(glue_refuse), at_sender=True)
    except KeyError:
      pass
    try:
      content = readInfo("data/long.json")
      my_long = de(str(content[group][qq]))
      group_hit_glue[group][qq]['time'] = time.time()
      probability = random.randint(1, 100)
      if 0 < probability <= 10:
        reduce = random_long()*2
        my_long = my_long + reduce
        result = random.choice([
          f"你打了个爽！触发双倍长度奖励！牛子增加了{format(reduce,'.2f')}cm！！！",
          f"你打了个舒服痛快的胶呐，牛子增加了{format(reduce,'.2f')}cm！"
          ])
      elif 10 < probability <= 50:
        reduce = random_long()
        my_long = my_long + reduce
        result = random.choice([
          f"你嘿咻嘿咻一下，促进了牛子发育，牛子增加了{format(reduce,'.2f')}cm！",
          f"你在众目睽睽下打完了胶，你的牛子在众人震惊的目光下增加了{format(reduce,'.2f')}cm！"
          ])
      elif 50 < probability <= 70:
        result = random.choice([
          "你打了个胶，但是什么变化也没有，好奇怪捏~",
          "你的牛子刚开始变长了，可过了一会又回来了，什么变化也没有，好奇怪捏~"
          ])
      else:
        reduce = random_long()
        my_long = my_long - reduce
        if my_long < 0:
          result = random.choice([
            f"你已经变成女生了哦！你的牛子凹进去了{format(reduce,'.2f')}cm！",
            f"你突发恶疾！你的牛子凹进去了{format(reduce,'.2f')}cm！",
            f"笑死，你因为打胶过度导致牛子凹进去了{format(reduce,'.2f')}cm！"
          ])
        else:
          result = random.choice([
            f"小打怡情，大打伤身，强打灰飞烟灭！你过度打胶，牛子缩短了{format(reduce,'.2f')}cm捏！",
            f"你的牛子变长了许多，你很激动地继续打胶，但是牛子不但没变长还缩短了{format(reduce,'.2f')}cm！",
    f"阿哦，你过度打胶，牛子缩短{format(reduce,'.2f')}cm了呢！"
            ])
      content[group][qq] = my_long
      readInfo('data/long.json',content)
    except KeyError:
      del group_hit_glue[group][qq]['time']
      result = random.choice([
        "你还没有牛子呢！不能打胶！请发送 注册牛子",
        "无牛子，打胶不要的，请发送 注册牛子"
        ])
    finally:
      await niuzi_hit_glue.finish(Message(result),at_sender=True)
