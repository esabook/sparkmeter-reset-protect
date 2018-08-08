from utils.setting import setting as s
import telegram, json

bot = telegram.Bot(token=s().Data['telegram_bot_token'])
timeoutVal=100
class telegram_bot():

    def sendDocToAllRegisteredChannel(self, filePath):
        uploadedFile = {}
        for Id in self._getAllChatId():
            if filePath in uploadedFile.keys():
                filePath = uploadedFile[filePath]
            fileId = self._sendDocument(Id, filePath)
            uploadedFile[filePath] = fileId
    def sendMessageToAllRegisteredChannel(self, message):
        for Id in self._getAllChatId():
            try:
                self._sendMessage(Id, message)
            except:
                pass

    def _sendDocument(self, chatId, filePath):
        doc = bot.send_document(chat_id = chatId, document=open(filePath, 'rb', timeout = timeoutVal))
        return doc[1]['document']['file_id']


    def _sendMessage(self, chatId, message):
        print(message)
        try:        
            bot.send_message(chat_id=chatId, text=message, timeout = timeoutVal)
        except Exception as e:
            print('telegram_bot: _sendMessage: %s'%(e))
    


    def _getAllChatId(self):
        oo={}
        try:
            updates = bot.get_updates(timeout = timeoutVal)
            if len(updates)< 1 :
                return s().Data['telegram_chat_ids']
            for item in updates:
                try:
                    if ( item['channel_post']['chat']['id'] ):
                        oo[item['channel_post']['chat']['id']]=None
                    if ( item['message']['chat']['id'] ):
                        oo[item['message']['chat']['id']]=None
                except:
                    pass
            
            
        except Exception as e:
            print('telegram_bot: _getAllChatId: %s'%(e))
       
        return oo.keys()

