from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self.att_per_tour=None
        self.tour_per_att =None

        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        attrazioni={}
        tour={}

        for item in TourDAO.get_tour_attrazioni():
            tour_id = item['id_tour']
            attrazione_id = item['id_attrazione']

            if tour_id not in tour:
                tour[tour_id]=set()

            tour[tour_id].add(attrazione_id)

            if attrazione_id not in attrazioni:
                attrazioni[attrazione_id]=set()

            attrazioni[attrazione_id].add(tour_id)

        self.att_per_tour=tour
        self.tour_per_att=attrazioni


    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1


        tours_regione = [t for t in self.tour_map.values() if t.id_regione == id_regione]

        self._ricorsione(
            start_index=0,
            tours=tours_regione,
            pacchetto_parziale=[],
            durata_corrente=0,
            costo_corrente=0,
            valore_corrente=0,
            attrazioni_usate=set(),
            max_giorni=max_giorni,
            max_budget=max_budget)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo


    def _ricorsione(self, start_index, tours, pacchetto_parziale, durata_corrente,costo_corrente, valore_corrente, attrazioni_usate,max_giorni, max_budget):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = list(pacchetto_parziale)
            self._costo = costo_corrente

        for i in range(start_index, len(tours)):
            tour = tours[i]

            if max_giorni is not None and durata_corrente + tour.durata_giorni > max_giorni:
                continue

            if max_budget is not None and costo_corrente + tour.costo > max_budget:
                continue

            attrazioni_tour = self.att_per_tour.get(tour.id, set())

            if not attrazioni_tour.isdisjoint(attrazioni_usate):
                continue

            valore_da_aggiungere = sum(
                self.attrazioni_map[att].valore_culturale
                for att in attrazioni_tour
                if att not in attrazioni_usate)


            pacchetto_parziale.append(tour)
            nuove_attr = attrazioni_usate.union(attrazioni_tour)

            self._ricorsione(start_index=i+1,tours=tours, pacchetto_parziale=pacchetto_parziale,
                durata_corrente=durata_corrente + tour.durata_giorni,
                costo_corrente=costo_corrente + tour.costo,
                valore_corrente=valore_corrente + valore_da_aggiungere,
                attrazioni_usate=nuove_attr,
                max_giorni=max_giorni,
                max_budget=max_budget)

            pacchetto_parziale.pop()





