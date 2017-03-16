__author__ = 'setten'


import mechanize
import cookielib


class Browser(object):
    def __init__(self):
        # Browser
        self.br = mechanize.Browser()

        # Cookie Jar
        self.cj = cookielib.LWPCookieJar()
        self.br.set_cookiejar(self.cj)

        # Browser options
        self.br.set_handle_equiv(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        #br.set_debug_http(True)
        #br.set_debug_redirects(True)
        #br.set_debug_responses(True)

        # User-Agent (this is cheating, ok?)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]


class SiteWithForm(object):
    def __init__(self, url):
        self.base = url
        self.browser = Browser()

    def open(self):
        self.r = self.browser.br.open(self.base)
        self.html = self.r.read()


site = SiteWithForm(url="https://www2.esf.org/asp/form/address/login.asp")
site.open()

print site.html

# logging in
site.browser.br.select_form(nr=0)
site.browser.br.form['refnum'] = '5238'
site.browser.br.form['password'] = 'lltvwnji'
site.browser.br.submit()

p = [{'Nom': 'van Setten',
                 'Titre': 'Dr.',
                 "Prenom": "Michiel",
                 'Nationalite': 'NL',
                 'Sexe': 'M',
                 'Adresse1': 'Chemin des etoiles 8, bte L7.03.01',
                 'CodePostal': '1348',
                 'Ville': 'Louvain-la-Neuve',
                 'Pays': 'BE',
                 'EMail': 'mjvansetten@gmail.com'}]

participants = [
['Ali', 'Abedi', 'M', 'DE', 'Max-Planck-Institut fur Mikrostrukturphy', 'abedi@mpi-halle.mpg.de'],
['Ravikumar', 'Abhilash', 'M', 'IT', 'University of Milano Bicocca', 'a.ravikumar@campus.unimib.it'],
['Claudio', 'Attaccalite', 'M', 'FR', 'Instute Neel', 'claudio.attaccalite@gmail.com'],
['Xavier', 'Blase', 'M', 'FR', 'CNRS', 'xavier.blase@grenoble.cnrs.fr'],
['Gaelle', 'Bruant', 'M', 'FR', 'CNRS', 'gaelle.bruant@polytechnique.edu'],
['Jorge', 'Budagosky', 'M', 'ES', 'University of Zaragoza', 'jbudagosky@bifi.es'],
['Lucia', 'Caramella', 'F', 'IT', 'Dip. di Fisica - Universta di Milano', 'lucia.caramella@gmail.com'],
['Alberto', 'Castro', 'M', 'ES', 'BIFI', 'acastro@bifi.es'],
['Sophie', 'Chauvin', 'F', 'FR', 'Ecole polytechnique', 'sophie.chauvin@polytechnique.edu'],
['Andrea', 'Cucca', 'M', 'FR', 'LSI', 'andrea.cucca@polytechnique.edu'],
['Pier Luigi', 'Cudazzo', 'M', 'ES', 'Universidad del Pais Vasco', 'pierluigi.cudazzo@ehu.es'],
['Gabriele', 'D Avino', 'M', 'BE', 'Univeristy of Liege', 'gabriele.davino@gmail.com'],
['Thorsten', 'Deilmann', 'M', 'DE', 'Instut fur Festkorpertheorie', 'thorsten.deilmann@wwu.de'],
['Antoine', 'Dewandre', 'M', 'BE', 'University of Liege', 'antoine.dewandre@ulg.ac.be'],
['Marco', 'Di Gennaro', 'M', 'BE', 'university of Liege', 'mdigennaro@ulg.ac.be'],
['Matthias', 'Druppel', 'M', 'DE', 'University of Munster', 'm.drueppel@wwu.de'],
['Simon', 'Dubois', 'M', 'BE', 'IMCN/NAPS - UCLouvain', 'simon.dubois@uclouvain.be'],
['Carina', 'Faber', 'F', 'FR', 'Institut Neel CNRS', 'carina.faber@grenoble.cnrs.fr'],
['Michael', 'Friedrich', 'M', 'DE', 'Universitat Paderborn', 'Michael.Friedrich@uni-paderborn.de'],
['Giorgia', 'Fugallo', 'F', 'FR', 'LSI, ecole Polytechnique', 'giorgia.fugallo@gmail.com'],
['Johanna', 'I. Fuks', 'F', 'US', 'CUNY Hunter College', 'johannafuks@gmail.com'],
['Tobias', 'Forster', 'M', 'DE', 'University of Munster', 'tfoerster@wwu.de'],
['Pablo', 'Garcia-Gonzalez', 'M', 'ES', 'Universidad Autonoma de Madrid', 'pablo.garciagonzalez@uam.es'],
['Matteo', 'Gatti', 'M', 'FR', 'LSI Ecole Polytechnique Palaiseau', 'matteo.gatti@polytechnique.fr'],
['Christine', 'Giorgetti', 'F', 'FR', 'LSI-Ecole Polytechnique-CNRS', 'christine.giorgetti@polytechnique.edu'],
['Rex', 'Godby', 'M', 'UK', 'University of York', 'rex.godby@york.ac.uk'],
['Xavier', 'Gonze', 'M', 'BE', 'Universite Catholique de Louvain', 'xavier.gonze@uclouvain.be'],
['Eberhard', 'Gross', 'M', 'DE', 'MPI of Microstructure', 'Physics office.theory@mpi-halle.mpg.de'],
['Myrta', 'Gruning', 'F', 'UK', "Queen's University Belfast", 'm.gruening@qub.ac.uk'],
['Nicole', 'Helbig', 'F', 'DE', 'Forschungszentrum Julich', 'nehelbig@gmail.com'],
['Hannes', 'Huebener', 'M', 'UK', 'University of Oxford', 'hannes.huebener@gmail.com'],
['Jeiran', 'Jokar', 'M', 'DE', 'FZJ Juelich', 'j.jokar@fz-juelich.de'],
['Ksenia', 'Komarova', 'F', 'UK', 'Photochemistry Center', 'kgvladi@gmail.com'],
['Maximilian', 'Kulke', 'M', 'DE', 'Universitat Paderborn', 'kulke@mail.uni-paderborn.de'],
['Stefan', 'Kurth', 'M', 'ES', 'Univ. del Pais Vasco and IKERBASQUE', 'stefan.kurth@ehu.es'],
['Jonathan', 'Laflamme Janssen', 'M', 'BE', 'Universite catholique de Louvain', 'laflammejanssenjonathan@gmail.com'],
['He', 'Lin', 'M', 'IT', 'DIPARTIMENTO DI SCIENZA DEI MATERIALI', 'h.lin2@campus.unimib.it'],
['Mathias', 'Ljungberg', 'M', 'ES', 'DIPC, San Sebastian', 'mathias.ljungberg@gmail.com'],
['Neepa', 'Maitra', 'F', 'US', 'Hunter College CUNY New York', 'neepa.maitra@gmail.com'],
['Federico', 'Marchesin', 'M', 'ES', 'CFM - DIPC', 'federico_marchesin1@ehu.es'],
['Milagros', 'Medina', 'M', 'ES', 'Universidad de Zaragoza', 'mmedina@unizar.es'],
['Bernardo', 'Mendoza', 'M', 'IT', 'Centro de Investigaciones en Optica', 'bms@cio.mx'],
['Elena', 'Molteni', 'F', 'IT', "Universita' degli Studi di Milano", 'elena.molteni@unimi.it'],
['Victor', 'Moron', 'M', 'ES', 'EHU/UPV', 'vmorontejero@gmail.com'],
['Adriano', 'Mosca Conte', 'M', 'IT', 'University of Rome Tor Vergata', 'adriano.mosca.conte@roma2.infn.it'],
['Andrea', 'Neroni', 'F', 'DE', 'Forschungszentrum Juelich', 'a.neroni@fz-juelich.de'],
['Valerio', 'Olevano', 'M', 'FR', 'Institut Neel', 'valerio.olevano@neel.cnrs.fr'],
['Micael', 'Oliveira', 'M', 'BE', 'University of Liege', 'mjt.oliveira@ulg.ac.be'],
['Giovanni', 'Onida', 'M', 'IT', 'University of Milan - Physics Department', 'giovanni.onida@gmail.com'],
['Anna', 'Pikulska', 'F', 'PL', 'University of Warsaw', 'pikulska.anna@gmail.com'],
['Yann', 'Pouillon', 'M', 'ES', 'Universidad del Pais Vasco UPV/EHU', 'yann.pouillon@ehu.es'],
['Sriram', 'Poyyapakkam Ramkumar', 'M', 'BE', 'Universite Catholique de Louvain', 'sriram.ramkumar@uclouvain.be'],
['Lucie', 'Prussel', 'F', 'FR', 'Laboratoire des Solides Irradies', 'lucie.prussel@gmail.com'],
['Olivia', 'Pulci', 'F', 'IT', 'University of Rome Tor Vergata', 'olivia.pulci@roma2.infn.it'],
['Lucia', 'Reining', 'F', 'FR', 'ETSF/CNRS', 'lucia.reining@polytechnique.fr'],
['Francoise', 'Remacle', 'M', 'BE', 'University of Liege', 'FRemacle@ulg.ac.be'],
['Igor', 'Reshetnyak', 'M', 'FR', 'Ecole Polytechnique', 'igor.reshetnyak@polytechnique.edu'],
['Gian-Marco', 'Rignanese', 'M', 'BE', 'Universite catholique de Louvain', 'gian-marco.rignanese@uclouvain.be'],
['Pina', 'Romaniello', 'F', 'FR', 'Universite Toulouse III', 'pina.romaniello@irsamc.ups-tlse.fr'],
['Tuomas', 'Rossi', 'M', 'FI', 'Aalto University', 'tuomas.rossi@aalto.fi'],
['Carlo Andrea', 'Rozzi', 'M', 'IT', 'CNR-NANO Modena', 'carloandrea.rozzi@nano.cnr.it'],
['Doris', 'Ruiz', 'F', 'CL', 'University of Concepcion', 'doruiz@udec.cl'],
['Claudia', 'Rodl', 'F', 'FR', 'Ecole Polytechnique', 'claudia.roedl@polytechnique.edu'],
['Arno', 'Schindlmayr', 'M', 'DE', 'Universitat Paderborn', 'Arno.Schindlmayr@uni-paderborn.de'],
['Paolo', 'Silvestrini', 'M', 'IT', 'INFM', 'paolo.salvestrini@mi.infn.it'],
['Francesco', 'Sottile', 'M', 'FR', 'Ecole Polytechnique', 'francesco.sottile@polytechnique.fr'],
['Nicolas', 'Tancogne-Dejean', 'M', 'FR', 'Ecole Polytechnique', 'nicolas.tancogne-dejean@polytechnique.edu'],
['Walter', 'Tarantino', 'M', 'FR', 'LSI, Ecole Polytechnique Palaiseau', 'walter.tarantino@polytechnique.edu'],
['Ivano', 'Tavernelli', 'M', 'CH', 'EPFL', 'ivano.tavernelli@epfl.ch'],
['Marilena', 'Tzavala', 'F', 'FR', 'Ecole polytechnique', 'marilena.tzavala@polytechnique.edu'],
['Joost', 'VandeVondele', 'M', 'CH', 'ETH Zurich', 'joost.vandevondele@mat.ethz.ch'],
['Valerie', 'Veniard', 'F', 'FR', 'LSI Ecole Polytechnique CNRS', 'valerie.veniard@polytechnique.fr'],
['Matthieu', 'Verstraete', 'M', 'BE', 'University of Liege', 'matthieu.jean.verstraete@gmail.com'],
['Claudia', 'Violante', 'F', 'IT', 'University of Rome Tor Vergata', 'claudia.violante@roma2.infn.it'],
['Vojtech', 'Vlcek', 'M', 'DE', 'University of Bayreuth', 'vojtech.vlcek@gmail.com'],
['Marius', 'Wanko', 'M', 'ES', 'EHU/UPV San Sebastian', 'marius.wanko@gmail.com'],
['Hans-Christian', 'Weissker', 'M', 'FR', 'CINaM-CNRS Marseille', 'weissker@cinam.univ-mrs.fr'],
['Jianqiang', 'ZHOU', 'M', 'FR', 'ETSF-Palaiseau', 'jianqiang.zhou@polytechnique.edu'],
['Zeila', 'Zanolli', 'F', 'DE', 'Forschungszentrum Juelich', 'zeilazanolli@gmail.com'],
['Michiel', 'van Setten', 'M', 'BE', 'Universite Catholique de Louvain', 'mjvansetten@gmail.com'],
['Claudio', 'Verdozzi', 'M', 'SE', 'lund university', 'claudio.verdozzi@teorfys.lu.se']]


speakers = [
 ['Ali', 'Abedi', 'M', 'DE', 'Max-Planck-Institut fur Mikrostrukturphy', 'abedi@mpi-halle.mpg.de'],
 ['Xavier', 'Blase', 'M', 'FR', 'CNRS', 'xavier.blase@grenoble.cnrs.fr'],
 ['Jorge', 'Budagosky', 'M', 'ES', 'University of Zaragoza', 'jbudagosky@bifi.es'],
 ['Lucia', 'Caramella', 'F', 'IT', 'Dip. di Fisica - Universta di Milano', 'lucia.caramella@gmail.com'],
 ['Gabriele', 'D Avino', 'M', 'BE', 'Univeristy of Liege', 'gabriele.davino@gmail.com'],
 ['Marco', 'Di Gennaro', 'M', 'BE', 'university of Liege', 'mdigennaro@ulg.ac.be'],
 ['Simon', 'Dubois', 'M', 'BE', 'IMCN/NAPS - UCLouvain', 'simon.dubois@uclouvain.be'],
 ['Carina', 'Faber', 'F', 'FR', 'Institut Neel CNRS', 'carina.faber@grenoble.cnrs.fr'],
 ['Giorgia', 'Fugallo', 'F', 'FR', 'LSI, ecole Polytechnique', 'giorgia.fugallo@gmail.com'],
 ['Johanna', 'I. Fuks', 'F', 'US', 'CUNY Hunter College', 'johannafuks@gmail.com'],
 ['Rex', 'Godby', 'M', 'UK', 'University of York', 'rex.godby@york.ac.uk'],
 ['Myrta', 'Gruning', 'F', 'UK', "Queen's University Belfast", 'm.gruening@qub.ac.uk'],
 ['Nicole', 'Helbig', 'F', 'DE', 'Forschungszentrum Julich', 'nehelbig@gmail.com'],
 ['Hannes', 'Huebener', 'M', 'UK', 'University of Oxford', 'hannes.huebener@gmail.com'],
 ['Stefan', 'Kurth', 'M', 'ES', 'Univ. del Pais Vasco and IKERBASQUE', 'stefan.kurth@ehu.es'],
 ['Jonathan', 'Laflamme Janssen', 'M', 'BE', 'Universite catholique de Louvain', 'laflammejanssenjonathan@gmail.com'],
 ['Neepa', 'Maitra', 'F', 'US', 'Hunter College CUNY New York', 'neepa.maitra@gmail.com'],
 ['Milagros', 'Medina', 'M', 'ES', 'Universidad de Zaragoza', 'mmedina@unizar.es'],
 ['Bernardo', 'Mendoza', 'M', 'IT', 'Centro de Investigaciones en Optica', 'bms@cio.mx'],
 ['Elena', 'Molteni', 'F', 'IT', "Universita' degli Studi di Milano", 'elena.molteni@unimi.it'],
 ['Victor', 'Moron', 'M', 'ES', 'EHU/UPV', 'vmorontejero@gmail.com'],
 ['Andrea', 'Neroni', 'F', 'DE', 'Forschungszentrum Juelich', 'a.neroni@fz-juelich.de'],
 ['Anna', 'Pikulska', 'F', 'PL', 'University of Warsaw', 'pikulska.anna@gmail.com'],
 ['Francoise', 'Remacle', 'M', 'BE', 'University of Liege', 'FRemacle@ulg.ac.be'],
 ['Tuomas', 'Rossi', 'M', 'FI', 'Aalto University', 'tuomas.rossi@aalto.fi'],
 ['Claudia', 'Rodl', 'F', 'FR', 'Ecole Polytechnique', 'claudia.roedl@polytechnique.edu'],
 ['Ivano', 'Tavernelli', 'M', 'CH', 'EPFL', 'ivano.tavernelli@epfl.ch'],
 ['Joost', 'VandeVondele', 'M', 'CH', 'ETH Zurich', 'joost.vandevondele@mat.ethz.ch'],
 ['Matthieu', 'Verstraete', 'M', 'BE', 'University of Liege', 'matthieu.jean.verstraete@gmail.com'],
 ['Claudia', 'Violante', 'F', 'IT', 'University of Rome Tor Vergata', 'claudia.violante@roma2.infn.it'],
 ['Vojtech', 'Vlcek', 'M', 'DE', 'University of Bayreuth', 'vojtech.vlcek@gmail.com'],
 ['Zeila', 'Zanolli', 'F', 'DE', 'Forschungszentrum Juelich', 'zeilazanolli@gmail.com'],
 ['Michiel', 'van Setten', 'M', 'BE', 'Universite Catholique de Louvain', 'mjvansetten@gmail.com'],
]


for n in speakers:

    p = {'Nom': n[1],
         'Titre': 'Dr.',
         "Prenom": n[0],
         'Nationalite': n[3],
         'Sexe': n[2],
         'Adresse1': 'N.A.',
         'CodePostal': 'N.A.',
         'Ville': n[4],
         'Pays': n[3],
         'EMail': n[5],
         'Org': n[4]}

    l = site.browser.br.links(text_regex='Add a Sp').next()
    site.browser.br.follow_link(l)

    #for f in site.browser.br.forms():
    #    print f

    site.browser.br.select_form(nr=0)
    for k in p.keys():
        print k
        print p[k]
        if k in ['Titre', 'Nationalite', 'Sexe', 'Pays']:
            site.browser.br.form[k] = [p[k]]
        else:
            site.browser.br.form[k] = p[k]

    site.browser.br.submit(nr=1)

for l in site.browser.br.links():
    print l