# from transferService import TransferService
#
#
# transferService = TransferService('12341234')
# transferService.money_transfer(15.99, 'ServiceTest', 765445677654)
# tr_list = transferService.show_transfer_list()
# print(tr_list)

from sessionService import SessionService

serv = SessionService()
sesId = '127.0.0.1d15cced1a93e800c8c9a18729d779daa'
serv.add_session(sesId)
serv.add_client_to_session(sesId, 123)
serv.set_set_to_session(sesId, 4)
