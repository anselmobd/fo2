
from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

pprint(lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[0])

pprint(dict_conserto_lote_custom('172103161', '63', 'in', 222, username='anselmo_sis'))

row = lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[0]
pprint(row)

pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto']+222, username='anselmo_sis'))

pprint(dict_conserto_lote_custom('172103161', '63', 'in', 222, username='anselmo_sis'))

pprint(lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[0])

pprint(lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[:2])

for row in lotes.models.Lote.objects.filter(estagio=63, qtd=1, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[:2]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))

for row in lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[:10]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))

for row in lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[:100]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))

pprint(lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[0])

pprint(lotes.models.Lote.objects.filter(estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values()[0])

pprint(lotes.models.Lote.objects.filter(local__isnull=True, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('lote', 'qtd', 'conserto')[:2])

pprint(lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:10])

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:2]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:10]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:100]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:1000]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))

pprint(lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values()[0])
180201721

row = lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values()[0]
pprint(row)

pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd']-row['conserto'], username='anselmo_sis'))


for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:2]:
    pprint(row)

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:2]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd'], username='anselmo_sis'))

pprint(lotes.models.Lote.objects.filter(estagio=63).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values()[0])

pprint(lotes.models.Lote.objects.filter(lote='174908907').order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values()[0])

pprint(lotes.models.Lote.objects.filter(lote='180702057').order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values()[0])

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:2]:
    pprint(row)

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:2]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd'], username='anselmo_sis'))

pprint(lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[0])

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:10]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd'], username='anselmo_sis'))

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto')[:3000]:
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd'], username='anselmo_sis'))

for row in lotes.models.Lote.objects.filter(local__isnull=False, estagio=63, conserto=0).order_by('op', 'referencia', 'cor', 'ordem_tamanho', 'local', 'lote').values('local', 'lote', 'qtd', 'conserto'):
    pprint(dict_conserto_lote_custom(row['lote'], '63', 'in', row['qtd'], username='anselmo_sis'))


##########################################################################
# desendereçar 1
##########################################################################

from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

from fo2.connections import db_conn_so
cursor = db_conn_so().cursor()

from django.contrib.auth.models import User
usuario = User.objects.get(username='anselmo_sis')

lotes_desend = [
'200100826', 
]

for lote in lotes_desend:
    pprint(dict_conserto_lote_custom(
        cursor, lote, '63', 'out', 0, username='anselmo_sis'
    ))
    lote_rec = lotes.models.Lote.objects.get(lote=lote)
    lote_rec.local = None
    lote_rec.local_usuario = usuario
    lote_rec.save()

lotes_desend = [
# '191004270', 
# '191307165', 
# '191502351', 
# '191700458', 
# '194900996', 
# '200100826', 
'201005166', 
'201005255', 
'203809490', 
'204513092', '204513098', '204513165', '204513213', '204513217', '204513242', '204513493', '204513730', '204514005', '204514070', '204515255', '204516047', '204702048', '204702127', '204704578', '204904490', '204904607', '204904706', '204904802', '204908998', '204909372', '204909480', '204909747', '204910424', '204910721', '204910759', '204911538', '204919410', '204919411', '204919412', '205101437', '210200018', '210201886', '210202548', '210202563', '210210439', '210212579', '210214748', '210215712', '210216747', '210216766', '210217145', '210305436', '210504860', '210505553', '210505603', '210505858', '210505973', '210506335', '210506395', '210506450', '210506563', '210506748', '210506798', '210506799', '210506864', '210506865', '210506972', '210506974', '210507833', '210507945', '210508572', '210509205', '210509529', '210509560', '210509771', '210509856', '210510030', '210510130', '210510450', '210510574', '210510799', '210511063', '210511115', '210511116', '210511783', '210512035', '210512072', '210512088', '210512125', '210512145', '210512170', '210512450', '210512454', '210512582', '210512662', '210512699', '210512723', '210512792', '210803377', '210803475', '210901832', '210903394', '210904196', '210905430', '210905727', '210906599', '210906901', '210908328', '210909961', '210910043', '210910049', '210910211', '210910967', '210911196', '210911315', '210911714', '210911808', '210911812', '210911858', '210911859', '210911871', '210912908', '210913467', '210916717', '210916774', '210921663', '211000924', '211004077', '211004286', '211004288', '211004391', '211004549', '211004973', '211005633', '211009328', '211009397', '211009446', '211010499', '211010517', '211010573', '211013998', '211203828', '211302359', '211303050', '211304189', '211304934', '211404186', '211404261', '211404262', '211404799', '211406282', '211406345', '211406366', '211409692', '211500630', '211500641', '211500642', '211500645', '211500646', '211502886', '211503172', '211601576', '211601682', '211702022', '211801090', '211801147', '211801167', '211801197', '211801242', '211801272', '211803155', '211803263', '211803310', '211803331', '211803335', '211803337', '211803406', '211803453', '211803529', '211803544', '211803601', '211804833', '211805021', '211805171', '211806124', '211806159', '211806160', '211806515', '211806517', '211807517', '211807892', '211901899', '211901904', '211902126', '212002597', '212003208', '212004422', '212103627', '212502838', '212503818', '212503819', '212503820', '212503821', '212503822', '212503921', '212503944', '212503945', '212503963', '212503974', '212503975', '212503994', '212503996', '212503997', '212504000', '212504002', '212504006', '212504010', '212504015', '212504020', '212606209', '212609220', '212702967', '212702970', '212900802', '212901213', '212901286', '212901290', '212905433', '212906582', '213006476', '213010038', '213010065', '213101470', '213101479', '213101480', '213105061', '213105930', '213106527', '213106529', '213107786', '213110618', '213110651', '213110722', '213110739', '213110889', '213110947', '213111366', '213203852', '213203889', '213309638', '213309643', '213309644', '213309653', '213309685', '213309686', '213309690', '213309691', '213309699', '213309765', '213309766', '213502103', '213502105', '213507228', '213507290', '213508621', '213508624', '213508626', '213510281', '213513100', '213603995', '213603996', '213603998', '213604005', '213716530', '213716583', '213800231', '213808176', '213808183', '213808184', '213808196', '213808201', '213812361', '213812542', '213812566', '213812595', '213813039', '213813076', '213813150', '213813211', '213813282', '213813343', '213813425', '213813430', '213813515', '213813674', '213906203', '213906312', '213906313', '213906428', '213906523', '214008794', '214009343', '214009528', '214014681', '214015527', '214015636', '214016970', '214109904', '214112687', '214210385', '214210573', '214300013', '214300047', '214300048', '214300272', 
]

##########################################################################
# desendereçar 2
##########################################################################

from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

from fo2.connections import db_conn_so
cursor = db_conn_so().cursor()

from django.contrib.auth.models import User
usuario = User.objects.get(username='anselmo_sis')

lotes_desend = [
# '190503483',
'190506547',
'191307165',
'191402905',
'192606353',
'193207892',
]

for lote in lotes_desend:
    pprint(dict_conserto_lote_custom(
        cursor, lote, '63', 'out', 0, username='anselmo_sis'
    ))
    lote_rec = lotes.models.Lote.objects.get(lote=lote)
    lote_rec.local = None
    lote_rec.local_usuario = usuario
    lote_rec.save()

lotes_desend = [
# '190503483',
# '190506547',
# '191307165',
# '191402905',
# '192606353',
# '193207892',
'194304252',
'194307348',
'195004357',
'200204487', '200300655', '201002696', '201008875', '201012510', '201302678', '201305735', '202803545', '202804895', '203401923', '203910306', '203910931', '203913026', '204005212', '204007548', '204512276', '204514914', '204515054', '204515112', '204515390', '204515433', '204515451', '204515480', '204515533', '204515535', '204515568', '204515695', '204603961', '204604091', '204608660', '204702253', '204702415', '204903970', '204904192', '204905113', '204909201', '204910101', '204910562', '204911116', '204911224', '205002184', '205003683', '205005340', '205006241', '205006454', '205006601', '205006657', '205006661', '205100285', '205101499', '205101841', '205102687', '205103568', '210202387', '210202392', '210202400', '210202698', '210203194', '210210965', '210211146', '210212455', '210212456', '210212586', '210212653', '210213096', '210213447', '210213518', '210214040', '210215913', '210216487', '210216910', '210301672', '210405557', '210405833', '210500727', '210500728', '210501057', '210501196', '210501241', '210502006', '210504082', '210504296', '210504924', '210505050', '210505667', '210506509', '210507094', '210507095', '210507097', '210507189', '210507830', '210508158', '210509300', '210510015', '210510457', '210511161', '210511181', '210511418', '210512406', '210513162', '210513165', '210802996', '210903679', '210904947', '210906169', '210906770', '210907197', '210907923', '210908153', '210908875', '210909602', '210909976', '210911046', '210912346', '210918611', '210918620', '211002157', '211002808', '211004107', '211004165', '211004167', '211004262', '211005682', '211009762', '211009833', '211011734', '211011750', '211011751', '211011753', '211011754', '211011755', '211011756', '211011757', '211011758', '211011759', '211011819', '211011820', '211011821', '211011822', '211011823', '211011824', '211011825', '211011826', '211011951', '211011952', '211011953', '211101269', '211101526', '211101527', '211101537', '211205188', '211302833', '211302918', '211304056', '211402312', '211402313', '211402360', '211402361', '211402366', '211402368', '211402369', '211402451', '211402460', '211403307', '211405678', '211409636', '211409644', '211409680', '211501887', '211503779', '211703078', '211703447', '211801164', '211902136', '212003209', '212004436', '212004475', '212004500', '212205771', '212502802', '212503832', '212503926', '212504070', '212601975', '212607909', '212607911', '212702952', '212807603', '212900790', '212900796', '212905576', '212905646', '212905647', '212906749', '212906946', '212907089', '212907161', '212907211', '212907979', '212908124', '212908139', '213007688', '213007822', '213009893', '213010068', '213101277', '213101293', '213101468', '213107835', '213108117', '213108137', '213108138', '213108170', '213108184', '213108185', '213108201', '213108231', '213108318', '213109910', '213111239', '213111323', '213111362', '213302340', '213305727', '213309645', '213309718', '213309763', '213309782', '213500611', '213501636', '213506760', '213506906', '213506908', '213506909', '213506913', '213506916', '213506924', '213507066', '213507067', '213507113', '213510286', '213510287', '213510311', '213510312', '213510365', '213510434', '213510443', '213510458', '213510459', '213510460', '213510505', '213604237', '213709435', '213811887', '213812245',
'213812258',
'213813473',
'214109893',
'214210346',
]

# 2021-12-10

d-f1
. d-f2
export DEFAULT_SYSTEXTIL_DB=sn && export DJANGO_SETTINGS_MODULE=fo2.production_settings && export LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib/ && source /home/fo2_production/FabrilO2/venv/bin/activate && /home/fo2_production/FabrilO2/venv/bin/python /home/fo2_production/FabrilO2/src/manage.py shell

from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

from fo2.connections import db_conn_so
cursor = db_conn_so().cursor()

from django.contrib.auth.models import User
usuario = User.objects.get(username='anselmo_sis')

lotes_desend = [
'183506836',
'183508395',
'184815366',
'190503626', '190503962', '191406640', '191407267', '195007155', '200100841', '200100844', '200100918', '200102410', '200102450', '200102543', '200102595', '201305863', '201800171', '202803548', '202901272', '203001524', '203607582', '203910499', '203914828', '203914920', '203914922', '204007930', '204008424', '204015027', '204513318', '204513677', '204515074', '204515290', '204515613', '204516004', '204604389', '204604652', '204604672', '204605000', '204605089', '204605301', '204605399', '204605587', '204605630', '204605671', '204605784', '204605873', '204903416', '204903672', '204903702', '204904074', '204904124', '204904263', '204908330', '204908414', '204908559', '204908876', '204909251', '204919420', '205003564', '205003700', '205003704', '205004223', '205004383', '205004442', '205005683', '205005812', '205008881', '205101391', '205101409', '205102097', '205102637', '205102870', '205200096', '205200163', '210201591', '210202265', '210203102', '210203921', '210204514', '210205763', '210206009', '210209881', '210209994', '210210675', '210210679', '210210899', '210210964', '210210966', '210211047', '210212446', '210212856', '210213045', '210213070', '210213188', '210213228', '210213264', '210213333', '210215289', '210215487', '210216607', '210216686', '210216814', '210216860', '210216862', '210217042', '210217162', '210217191', '210300111', '210501097', '210501183', '210501878', '210502079', '210504947', '210505778', '210506039', '210506541', '210507736', '210508299', '210511104', '210511180', '210511698', '210511837', '210511857', '210512055', '210512073', '210512171', '210512540', '210512858', '210513129', '210601309', '210601355', '210601512', '210601756', '210602105', '210903026', '210903062', '210903238', '210903254', '210903294', '210903677', '210903823', '210904594', '210904895', '210905338', '210907657', '210908420', '210908939', '210909037', '210910915', '210911192', '210912542', '210912603', '210912607', '211001450', '211001579', '211001975', '211002138', '211004490', '211005519', '211009251', '211009382', '211009385', '211102214', '211400627', '211405792', '211406283', '211501895', '211501909', '211503014', '211503086', '211801787', '211801836', '211801974', '211802087', '211802093', '211802192', '211802193', '211803228', '211803422', '211803426', '211804342', '211804618', '211805075', '211805083', '211805110', '211805193', '211805194', '211805394', '211806150', '211806486', '211807880', '211902130', '211906925', '212601983', '212607769', '212607881', '212607896', '212607950', '212702969', '212703069', '212801965', '212801969', '212900783', '212900874', '212906303', '212906359', '212906916', '212907008', '212907148', '212907429', '212907913', '212907919', '212908051', '212908085', '212908142', '213007590', '213009970', '213104886', '213105625', '213105883', '213106294', '213106335', '213106377', '213107781', '213108328', '213109666', '213109986', '213110411', '213110413', '213110414', '213203890', '213302427', '213302592', '213502414', '213507070', '213510442', '213716582', '213813063', '213813518', '213815397',
'214109983',
'214210372',
'214210438',
'214210478',
]

for lote in lotes_desend[2:]:
    pprint(dict_conserto_lote_custom(
        cursor, lote, '63', 'out', 0, username='anselmo_sis'
    ))
    lote_rec = lotes.models.Lote.objects.get(lote=lote)
    lote_rec.local = None
    lote_rec.local_usuario = usuario
    lote_rec.save()

# 2021-12-14 13h01

d-f1
. d-f2
export DEFAULT_SYSTEXTIL_DB=sn && export DJANGO_SETTINGS_MODULE=fo2.production_settings && export LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib/ && source /home/fo2_production/FabrilO2/venv/bin/activate && /home/fo2_production/FabrilO2/venv/bin/python /home/fo2_production/FabrilO2/src/manage.py shell

from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

from fo2.connections import db_conn_so
cursor = db_conn_so().cursor()

from django.contrib.auth.models import User
usuario = User.objects.get(username='anselmo_sis')

lotes_desend = [
'194806614',
'200501008',
'203001546',
'204903550', '205005658', '205005867', '210210876', '210210878', '210211034', '210211110', '210211223', '210211801', '210214645', '210214952', '210215760', '210215912', '210216050', '210216587', '210216702', '210216768', '210502012', '210502056', '210504197', '210504252', '210505941', '210506008', '210506037', '210507632', '210507770', '210510146', '210512790', '210513195', '210513199', '210513253', '210600326', '210600327', '210605989', '210902533', '210902539', '210902643', '210903098', '210903133', '210903773', '210904891', '210904894', '210906165', '210912540', '210912552', '210912596', '210912740', '210913672', '210913673', '210913674', '210913737', '210913752', '210913753', '210913754', '210913766', '211001449', '211001716', '211004575', '211008378', '211008488', '211008594', '211009787', '211009788', '211009837', '211009838', '211009860', '211009861', '211303072', '211303083', '211303084', '211303093', '211303094', '211303095', '211304100', '211402858', '211402875', '211403714', '211403723', '211501637', '211501638', '211601577', '211601668', '211601680', '211601691', '211601714', '211700045', '211700046', '211700089', '211700090', '211700091', '211700092', '211700093', '211700094', '211700095', '211803233', '211803471', '211803685', '211804408', '211804516', '211804696', '211805114', '211805187', '211806938', '211807714', '212002722', '212002745', '212003153', '212003154', '212003458', '212004494', '212503242', '212600489', '212600490', '212600498', '212600499', '212600507', '212600508', '212600516', '212600517', '212600518', '212600519', '212600533', '212600534', '212600535', '212600536', '212602056', '212606302', '212607709', '212702968', '212703044', '212703048', '212703253', '212900788', '212900794', '212906295', '212906299', '212906542', '212906815', '212907107', '212907430', '212908015', '212908104', '213000267', '213000268', '213000269', '213000270', '213000271', '213000272', '213000273', '213000274', '213000275', '213000276', '213000296', '213000297', '213000298', '213000299', '213000300', '213000301', '213000302', '213000303', '213000304', '213000305', '213000325', '213000326', '213000327', '213000328', '213000329', '213000330', '213000331', '213000332', '213000333', '213000334', '213000354', '213000355', '213000356', '213000357', '213000358', '213000359', '213000360', '213000361', '213000362', '213000363', '213000402', '213000403', '213000419', '213000420', '213000437', '213000483', '213000484', '213000485', '213000500', '213000501', '213000502', '213000517', '213000518', '213000519', '213000534', '213000535', '213000536', '213000551', '213000552', '213000553', '213000554', '213000555', '213000556', '213000594', '213000596', '213000605', '213000606', '213007662', '213007676', '213007677', '213007758', '213100236', '213100237', '213100238', '213100239', '213100240', '213100241', '213100242', '213100256', '213100257', '213100258', '213100259', '213100260', '213100261', '213100262', '213100276', '213100277', '213100278', '213100279', '213100280', '213100281', '213100282', '213100296', '213100297', '213100298', '213100299', '213100300', '213100301', '213100302', '213101295', '213101349', '213101350', '213101467', '213101481', '213105835', '213108001', '213108099', '213108420', '213109584', '213109668', '213110484', '213110486', '213110847', '213203687', '213203780', '213203781', '213203961', '213204021', '213302112', '213302342', '213302377', '213302378', '213303349', '213502235', '213506774', '213511683', '213600045', '213600049', '213600050', '213600051', '213600055', '213600056', '213600079', '213600082', '213600087', '213600088', '213600098', '213600101', '213600102', '213600115', '213600116', '213600185', '213600186', '213600188', '213600189', '213600193', '213600194', '213600195', '213600196', '213600204', '213600209', '213600210', '213600217', '213600218', '213600219', '213600220', '213600223', '213600224', '213600310', '213600311', '213600322', '213600323', '213600324', '213600325', '213603833', '213716533', '213800218', '213800224', '213800225', '213800226', '213811600', '213811602', '213811656', '213811811', '213812360', '213812558', '213812559', '213812599', '213813279', '213813372', '213813713', '213813717', '213813718', '213813788', '213813944', '213814017', '214210316', '214210389', '214210433', '214210462', '214210464', '214210483', '214210496', '214210513', '214300002', '214300003', '214300008', '214300009', '214300010', '214300011', '214300014', '214300015', '214300031', '214300032', '214300033', '214300034', '214300043', '214300044',
'214300045',
'214300046',
]

len(lotes_desend)

for lote in lotes_desend:
    pprint(dict_conserto_lote_custom(
        cursor, lote, '63', 'out', 0, username='anselmo_sis'
    ))
    lote_rec = lotes.models.Lote.objects.get(lote=lote)
    lote_rec.local = None
    lote_rec.local_usuario = usuario
    lote_rec.save()

# 2021-12-15 16h16

d-f1
. d-f2
export DEFAULT_SYSTEXTIL_DB=sn && export DJANGO_SETTINGS_MODULE=fo2.production_settings && export LD_LIBRARY_PATH=/usr/lib/oracle/12.2/client64/lib/ && source /home/fo2_production/FabrilO2/venv/bin/activate && /home/fo2_production/FabrilO2/venv/bin/python /home/fo2_production/FabrilO2/src/manage.py shell

from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

from fo2.connections import db_conn_so
cursor = db_conn_so().cursor()

from django.contrib.auth.models import User
usuario = User.objects.get(username='anselmo_sis')

lotes_desend = [
'184408254',
'201504034',
'204005903',
'204513755',
'204514607',
'204515095',
'204515283',
'204604018',
'204605628',
'204608808',
'204904258',
'204904596',
'204909517',
'205000071',
'205002582',
'205004115',
'205006259',
'205006711',
'205100391',
'205101438',
'205102099',
'210107705',
'210203123',
'210203605',
'210203692',
'210209915',
'210210109',
'210210312',
'210210390',
'210210731',
'210216735',
'210301760',
'210602013',
'210602106',
'210605739',
'210905730',
'210906403',
'210911127',
'210911702',
'210912283',
'210912609',
'211005023',
'211005547',
'211008595',
'211010624',
'211010625',
'211102249',
'211102330',
'211302757',
'211302919',
'211403250',
'211404358',
'211503160',
'211503173',
'211702168',
'211703554',
'211802250',
'211803472',
'211805113',
'211805115',
'211806390',
'211806420',
'211901897',
'211901901',
'211901905',
'211901906',
'211901907',
'211905476',
'212004408',
'212600095',
'212607778',
'212609338',
'212609399',
'212609429',
'212802651',
'212807316',
'212906741',
'212908049',
'213000183',
'213000184',
'213105624',
'213108232',
'213108325',
'213108390',
'213108439',
'213110412',
'213111343',
'213203821',
'213302348',
'213302903',
'213303154',
'213506758',
'213506901',
'213511492',
'213511522',
'213811565',
'213815377',
'213906524',
'213918740',
'213918741',
'214022600',
'214022601',
'214022624',
'214022689',
'214022752',
'214022786',
'214110504',
'214210352',
]

len(lotes_desend)

for lote in lotes_desend:
    pprint(dict_conserto_lote_custom(
        cursor, lote, '63', 'out', 0, username='anselmo_sis'
    ))
    lote_rec = lotes.models.Lote.objects.get(lote=lote)
    lote_rec.local = None
    lote_rec.local_usuario = usuario
    lote_rec.save()

##########################################################################
# desendereçar 2 !! na verdade apenas tira do conserto
##########################################################################

from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

from fo2.connections import db_conn_so
cursor = db_conn_so().cursor()

from django.contrib.auth.models import User
usuario = User.objects.get(username='anselmo_sis')

lotes_desend = [
    # '172103161',
    '175200009',
]

for lote in lotes_desend:
    pprint(dict_conserto_lote_custom(
        cursor, lote, '63', 'out', 0, username='anselmo_sis'
    ))

def do_arq():
    with open("desliga_cd_lotes.txt") as file_in:
        lin_idx = 0
        for line in file_in:
            lin_idx += 1
            if lin_idx >= lin_ini+lin_count:
                break
            elif lin_idx >= lin_ini:
                lote = line[2:11]
                # print(lote)
                pprint(dict_conserto_lote_custom(
                    cursor, lote, '63', 'out', 0, username='anselmo_sis'
                ))

lin_ini = 8213
lin_count = 2000
do_arq()

##########################################################################
# tira tudo do conserto - 2022-04-03
##########################################################################

from pprint import pprint
import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote_custom

from fo2.connections import db_conn_so
cursor = db_conn_so().cursor()

from django.contrib.auth.models import User
usuario = User.objects.get(username='anselmo_sis')

from collections import namedtuple


pprint(dict_conserto_lote_custom(
    cursor, '201803445', '63', 'out', 0, username='anselmo_sis'
))
pprint(dict_conserto_lote_custom(
    cursor, '191402902', '63', 'out', 0, username='anselmo_sis'
))


sql = """
    SELECT DISTINCT 
      l.PERIODO_PRODUCAO PER
    , l.ORDEM_CONFECCAO OC
    FROM PCPC_040 l
    WHERE 1=1
      AND l.QTDE_CONSERTO <> 0
      AND l.CODIGO_ESTAGIO = 63
"""
dados = list(cursor.execute(sql))
pprint(dados[:2])

Lote = namedtuple('Lote', ['per', 'oc'])

lotes = []
for row in dados:
    lotes.append(
        "{lote.per}{lote.oc:05}".format(lote=Lote(*row))
    )

pprint(lotes[:2])

for idx, lote in enumerate(lotes[:1000]):
    print(idx+1)
    pprint(dict_conserto_lote_custom(
        cursor, lote, '63', 'out', 0, username='anselmo_sis'
    ))





