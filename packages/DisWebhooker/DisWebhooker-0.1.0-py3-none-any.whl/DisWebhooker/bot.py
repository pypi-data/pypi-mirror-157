import asyncio
import inspect
import discord
import traceback
import json

from typing import Any

from discord.ext import commands

from .clients  import Clients
from .command  import BaseCommand
from .commands import commands as webcommands
from .errors   import CommandError,EmptyCommand
from .webhook  import webhook, webhookIO
### hibot
from DisWebhooker.func import Getavatar
from DisWebhooker.webhook import hiWebhook

def lister(func):
	argsspec = inspect.getfullargspec(func)
	_ = []
	_ += argsspec.args
	if argsspec.varargs:
		_ += "*"
		_ .append ( argsspec.varargs )
	return _,argsspec.defaults

async def passer(func,defaults,*args,**kw):
	if not args:
		args+=defaults
	return await func(*args,**kw)

class bot(object):
	def __init__(self, webhook: webhook,commands: webcommands,core: BaseCommand=BaseCommand):
		super(bot, self).__init__()
		self.webhook  = webhook
		self.commands = commands
		self.command_prefix = commands.command_prefix
		self.BaseCommand = core(prefix=self.command_prefix)
		if commands.help_command is None:
			async def help_command(self,ctx):
				return await webhook.send(f"\n```\n{commands.help_message()}\n```\n")
			self.add_command(help_command,name="help",description="show this help message")
	def command(self,*args,**kw):
		def inner(func):
			args_ = ()
			li = list(args_)
			li.append(func)
			return self.commands.add_command(li[0],**kw)
		return inner
	def remove_command(self,command,**kw):
		self.commands.remove_command(command,**kw)
	def add_command(self,command,**kw):
		self.commands.add_command(command,**kw)
	def replace_command(self,command,**kw):
		self.commands.replace_command(command,**kw)
	async def call_command(self,name,*args,**kw):
		return await self.commands.awaitit_command(self,name,*args,**kw)
	def Get_word(self,BC,command):
		COMMAND,SELFCOMMAND      =  BC.GetCmd(command=command)
		return						BC.Get_(view=COMMAND),SELFCOMMAND
	def getInfo(self,message,content):
		if not content.startswith(self.command_prefix):
			return
		BC  = self.BaseCommand
		name = self.Get_word(BC,content)
		try:
			func = self.commands.get_func(name[0])
		except EmptyCommand:
			return None
		EvalArgs,defaults = lister(func)
		BCPC = BC.process_command(command=content,EA=EvalArgs[2:]) # EA: Eval Args
		ArgsVar = ()
		var = tuple(BCPC["VARIABLES"].values())
		ArgsVar += (self,message,*var)
		try:
			return (passer,(func,defaults,*ArgsVar))
		except Exception as e:
			raise CommandError("unexpected error -:- Exception: %s" % e)
		return None

	async def process_command(self,message,content):
		everything = self.getInfo(message,content)
		if everything is None:
			return
		try:
			return asyncio.create_task(everything[0](*everything[1]))
		except Exception as e:
			raise CommandError("unexpected error -:- Exception: %s" % e)
	def add_listen(self,func,name=None):
		return self.listen(name=name)(func)
	def remove_listen(self,func,name=None):
			name = func.__name__ if name is None else name
			if not __import__("asyncio").iscoroutinefunction(func):
				raise TypeError('Listeners must be coroutines')
			if name in self.extra_events:
				try:
					self.extra_events[name].remove(func)
				except ValueError:
					pass
	def listen(self,*args,**kw):
		def inner(func):
			name = func.__name__ if kw.get("name",None) is None else kw.get("name")
			if not __import__("asyncio").iscoroutinefunction(func):
				raise TypeError('Listeners must be coroutines')
			if name in self.extra_events:
				self.extra_events[name].append(func)
			else:
				self.extra_events[name] = [func]
		return inner
	def event(self,func,*args,**kw):
		return self.listen(*args,**kw)(func)
	async def send(self,*args,**kw):
		return await self.webhook.send(*args,**kw)

class Bot(bot):
	def __init__(self ,*, command_prefix,Id_Token=None,setuped = False,**kw):
		super(bot,self).__init__()
		self.commands = webcommands(command_prefix=command_prefix)
		self.command_prefix = self.commands.command_prefix
		self.BaseCommand = BaseCommand(prefix=command_prefix)
		self.extra_events = {}
		if self.commands.help_command is None:
			async def help_command(self,ctx):
				return await self.webhook.send(f"\n```\n{self.commands.help_message()}\n```\n")
			self.add_command(help_command,name="help",description="show this help message")
		if Id_Token is not None:
			self.setup(*Id_Token) if not setuped else self.IO(**kw)
		elif Id_Token is None and setuped:
			self.IO(**kw)
	def GetWebhook(self):
		return self.webhook
	def IO(self,**kw):
		self.webhook = webhookIO(**kw)
		self.name	= self.webhook.username
		self.avatar	= self.webhook.avatar
		self.id     = "0"
		self.discriminator =  self.webhook.discriminator
		self.user   = self.name+"#"+self.discriminator if self.name is not None else None
		return self.webhook
	def setup(self,Id,Token,**kw):
		self.webhook  = webhook(Id,Token,**kw)
		self.name	= self.webhook.username
		self.avatar	= self.webhook.avatar
		self.id     = self.webhook.id
		self.discriminator =  self.webhook.discriminator
		self.user   = self.name+"#"+self.discriminator if self.name is not None else None
		return self.webhook



class hibot(Clients):
	igonre = None
	def dispatch(self, event_name: str, /, *args: Any, **kwargs: Any) -> None:
		# super() will resolve to Client
		super().dispatch(event_name, *args, **kwargs)  # type: ignore
		ev = 'on_' + event_name
		self.webhooksdispatchs(ev, *args, **kwargs)
		for event in self.extra_events.get(ev, []):
			self._schedule_event(event, ev, *args, **kwargs)  # type: ignore
	# event handler
	def webhook_schedule_event(self,event, bot, *args, **kwargs):
		try:
			# run the event func
			return __import__("asyncio").create_task(event(bot,*args,**kwargs))
		except Exception as e:
			if self.igonre:
				print("igonre Exception in webhookHandler",e.__class__.__name__,e,sep=": ")
			elif self.igonre is None:
				traceback.print_exc()
			else:
				raise e
	def webhooksdispatchs(self,event_name,/,*args,**kwargs):
		#loop webhook and dispatch them
		for webhook in self.webhooks.children:
			_, bot = self.webhookObject(webhook)
			for event in bot.extra_events.get(event_name,[]):
				self.webhook_schedule_event(event, bot, *args, **kwargs)
	# handle one webhook
	async def webhookHandler(self,webhookobj,message):
		_,obj = self.webhookObject(webhookobj)
		data = obj.webhook.get().data
		try:
			kw = {"name":data["name"],"avatar":Getavatar(data["id"],data["avatar"])} if data["avatar"] is not None else {"name":data["name"],"avatar":None}
		except TypeError as e:
			if str( e ) == "can only concatenate str (not \"NoneType\") to str":
				kw = {"name":data["name"],"avatar":None}
			else:
				raise e
		channel = message.channel
		if not isinstance(channel,discord.TextChannel):
			print("get a message from non-TextChannel {0}".format(message))
			return None
		webhooks_ = await channel.webhooks()
		if list(await channel.webhooks()) != []:
			web = webhooks_[0]
			w_w = hiWebhook(web.url,username=kw["name"],avatar=kw["avatar"])
		else:
			web = await channel.create_webhook(name="webhooker-webhook")
			w_w = hiWebhook(web.url,username=kw["name"],avatar=kw["avatar"])

		#_webhook_ = obj.webhook
		obj.webhook = w_w
		try:
			processing = await obj.process_command(message,message.content)
			#obj.webhook = _webhook_
			return processing
		except Exception as e:
			#obj.webhook = _webhook_
			raise e
	#handler for on_message
	async def webhooks_handler(self,message):
		for webhook in self.webhooks.children:
			try:
				asyncio.create_task(self.webhookHandler(webhook,message))
			except Exception as e:
				if self.igonre:
					print(f"igonre Exception in {self.webhookHandler}",e.__class__.__name__,e,sep=": ")
				elif self.igonre is None:
					traceback.print_exc()
				else:
					raise e
	commands.Cog.listener()
	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))

	commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		asyncio.create_task(self.webhooks_handler(message))
		return await self.process_commands(message)

		# print auther && id && content
		#print("Message from {0.author}:{0.author.id}-:-[\"{0.content}\"]".format(message)) 


class lowbot(Clients):
	commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot:
			return
		for webhook in self.webhooks.children:
			_,o = self.webhookObject(webhook)
			return await o.process_command(message,message.content)
		await self.process_commands(message)

		# print auther && id && content
		#print("Message from {0.author}:{0.author.id}-:-[\"{0.content}\"]".format(message)) 


