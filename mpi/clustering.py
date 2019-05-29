import math
import numpy as np
from mpi4py import MPI
import csv
import os

# konwencja:
# przy zmiejszaniu tablicy klastrow, usredniony wynik zapisujemy w komorkach o nizszym indeksie, a te o wyzszym usuwamy
# wezel o indeksie 0 to master
# przy laczeniu dwoch klastrow, nowoutworzony klaster otwrzymuje indeks po rodzicu, ktorego indeks byl nizszy
# pierwszy i ostatni komputer warto zeby byly najszybsze:
# pierwszy ze wzgledu na to, ze w kilku miejscach cala reszta musi czekac na niego,
#  drugi ze wzg;edu na to, ze zazwyczaj musi wyliczyc o 1-2 odleglosci wiecej


MPIcomm = MPI.COMM_WORLD  # zmienna sluzaca do wywolywania funkcji MPI; laczy wszystkie wezly
MPIrank = MPIcomm.rank  # zmienna przechowujaca indeks danego wezla
MPIsize = MPIcomm.size  # zmienna przechowujaca liczbe wszystkich wezlow

# nazwa input-pliku data.csv
filename = 'data.csv'
for root, dirs, files in os.walk('.'):
    if filename in files:
        filename = os.path.join(root, filename)

data_file = open(filename, 'r')
clusters_str = list(csv.reader(data_file))
clusters = [[0 for i in range(len(clusters_str[j]))] for j in range(len(clusters_str))]

for j in range(len(clusters_str)):
    for i in range(len(clusters_str[j])):
        clusters[j][i] = float(clusters_str[j][i])

numberOfPoints = len(clusters)
# clusters = [[0,2], [2,4], [3,5], [4,6], [5,7],                  # lista przechowujaca wspolrzedne wszystkich
# klastrow ( zmienia sie z kazda iteracja ) [1.5, 1.8],[2.5, 2.8],[3.5, 3.8],[4.5, 4.8],[5.5, 5.8], [5, 8],[6, 9],[7,
# 1],[8, 2],[9, 3], [8, 8], [9, 9], [1, 1], [2, 2],[3, 3], [1, 0.6],[2, 1.6],[3, 2.6],[4, 3.6],[5, 4.6], [9, 11],[1,
# 2],[3, 4],[5, 6],[7, 8]]

'''numberOfPoints = 10
clusters =  [[0,1], [1,3], [2,6], [3,10], [4,15],
            [5,21], [6,28], [7,36], [8,45], [9,55]]'''

'''numberOfPoints = 5
clusters = [[4,15], [3,10], [2,6], [1,3], [0,1]]'''

numberOfClusters = numberOfPoints  # wskazuje aktualna liczbe klastrow

distances = []  # lista list dystansow miedzy klastrami
# Jest w ksztalcie trojkata: "i"-ty wiersz posiada "i" rekordow
# przyklad dla 4 klastrow ("x" oznacza jakas wartosc)
#   0 1 2 3
# 0
# 1 x
# 2 x x
# 3 x x x

for i in range(0, numberOfClusters):  # inicjalizacja listy list dystansow zerami
    tmp_list = []
    for j in range(0, i):
        tmp_list.append(0)
    distances.append(tmp_list)

joins = []  # lista kolejnych zlaczen; wynik dzialania programu
shortestDistance = [0, 0, float('inf')]  # najkrotszy dystans zapamietany przez wszystkie wezly


# Wskazuje podzial przeszukiwanej listy dystansow dla wezlow-robotnikow lower - dolna granica, indeks pierwszego
# dystansu na liscie ( powinien byc zawsze rowny 0 ) upper - gorna granica, indeks gornego dystansu na liscie (
# powinien byc zawsze numberOfDistances - 1 ) nodeNo - numer wezla ( uwaga: wezel 0 to master, wszystkie inne zajmuja
# sie wyliczaniem i wlasnie ich indeksy podajemy jako argument ) nodesAmout - liczba wszystkich wezlow ( lacznie z
# masterem )
def count_limits_for_finding_the_lightest_distance(lower, upper, node_no, nodes_amount):
    lower_limit = (node_no - 1) * (upper - lower) / (nodes_amount - 1)  # nodeAmount - 1 zeby nie wliczac mastera
    upper_limit = (node_no * (upper - lower) / (nodes_amount - 1))  #
    if node_no + 1 == nodes_amount:  # zeby przeliczyc caly zbior, ostani wezel musi policzyc o jeden element wiecej
        upper_limit += 1
    return [int(math.floor(lower_limit)), int(math.floor(upper_limit))]


# Wskazuje przedzial listy wspolrzednych klastrow, dla ktorych wezly-robotnicy beda wyliczac odleglosc od
# nowoutworzonego klastra lower - dolna granica, indeks pierwszego dystansu na liscie ( powinien byc zawsze rowny 0 )
# upper - gorna granica, indeks gornego dystansu na liscie ( powinien byc zawsze numberOfDistances - 1 ) nodeNo -
# numer wezla ( uwaga: wezel 0 to master, wszystkie inne zajmuja sie wyliczaniem i wlasnie ich indeksy podajemy jako
# argument ) nodesAmout - liczba wszystkich wezlow ( lacznie z masterem )
def countLimitsForCountingDistances(lower, upper, node_no, nodes_amount):
    lower_limit = (node_no - 1) * (upper - lower) / (nodes_amount - 1)  # nodeAmount - 1 zeby nie wliczac mastera
    upper_limit = (node_no * (upper - lower) / (nodes_amount - 1))
    return [int(lower_limit), int(upper_limit)]


# Wskazuje przedzial listy wspolrzednych klastrow, dla ktorych wezly-robotnicy beda wyliczac odleglosc od
# nowoutworzonego klastra za pierwszym razem lower - dolna granica, indeks pierwszego dystansu na liscie ( powinien
# byc zawsze rowny 0 ) upper - gorna granica, indeks gornego dystansu na liscie ( powinien byc zawsze
# numberOfDistances - 1 ) nodeNo - numer wezla ( uwaga: wezel 0 to master, wszystkie inne zajmuja sie wyliczaniem i
# wlasnie ich indeksy podajemy jako argument ) nodesAmout - liczba wszystkich wezlow ( lacznie z masterem )
def countLimitsForFirstCountingDistances(lower, upper, node_no, nodes_amount):
    lower_limit = (node_no - 1) * (upper - lower) / (nodes_amount - 1)  # nodeAmount - 1 zeby nie wliczac mastera
    upper_limit = (node_no * (upper - lower) / (nodes_amount - 1)) - 1  # - 1 zeby zbiory granice na siebie nie
    # nachodzily
    if node_no + 1 == nodes_amount:  # zeby przeliczyc caly zbior, ostani wezel musi policzyc o jeden element wiecej
        upper_limit += 1
    return [int(lower_limit), int(upper_limit)]


# wylicza pozycje komorki w trojkacie dystansow na podstawie jej indeksu;
# indexOfData - indeks wylicza sie tak, jakby dystansy byly dane byly zapisane w jedno wymiarowej liscie
def countCellPositionInDistancesTriangle(index_of_data):
    row = 1
    while row <= index_of_data:
        index_of_data -= row
        row += 1
    column = index_of_data
    return [row, column]


# liczy dystans miedzy dwoma punktami w przestrzeni o dowolnej liczbie dystansow
# p1, p2 - wspolrzedne punktow (kolejnosc podanych argumentow jest bez znaczenia
def countDistance(p1, p2):
    result = 0
    for i in range(0, len(p1)):
        result += (p1[i] - p2[i]) ** 2
    result = np.math.sqrt(result)
    return result


# wylicza dystasy miedzy kazda mozliwa para klastrow
# clusters - wskazuje wspolrzedne klastrow
# numberOfClusters - wskazuje liczbe klastrow
def countAllDistances(clusters, number_of_clusters):
    if MPIrank == 0:
        # wysylamy wspolrzedne klastrow wszystkim wezlom
        for i in range(1, MPIsize):
            MPIcomm.send(clusters, i)

        # zbieramy uzyskane wyniki i ustawiamy w odpowiednim miejscu w "distances"
        row = 1
        column = 0
        for i in range(1, MPIsize):
            recived = MPIcomm.recv(source=i, tag=0)
            for j in range(0, len(recived)):
                distances[row][column] = recived[j]
                column += 1
                # gdy dojdziemy do konca linii, przechodzimy do nastepnej
                if row == column:
                    row += 1
                    column = 0
    elif MPIrank > 0:
        # odbieramy wyslane klastry
        recived_clusters = MPIcomm.recv(source=0, tag=0)
        tmp_dist_list = []

        # ustalamy przedzialy dystansow do policzenia przez wezel-robotnika
        number_of_distances_to_count = 0
        for i in range(1, number_of_clusters):
            number_of_distances_to_count += i  # liczymy ile dystansow jest calkowicie do polaczenia
        limits = countLimitsForFirstCountingDistances(0, number_of_distances_to_count - 1, MPIrank,
                                                      MPIsize)  # i bierzemy odpowiedni zestaw dla danego wezla
        current_clusters_pair = countCellPositionInDistancesTriangle(
            limits[0])  # poruszamy sie po klastrze przy pomocy wskazanej pary
        end_clusters_pair = countCellPositionInDistancesTriangle(
            limits[1])  # konczymy obliczanie gdy obliczymy odleglosc dla ostatniej pary

        # obliczamy odleglosci na podstawie zadanego zestawu danych
        while True:
            dist = countDistance(recived_clusters[current_clusters_pair[0]], recived_clusters[current_clusters_pair[1]])
            tmp_dist_list.append(dist)
            # jezeli obliczylismy wartosci dla ostatniej pary, wychodzimy z petli
            if current_clusters_pair[0] == end_clusters_pair[0] and current_clusters_pair[1] == end_clusters_pair[1]:
                break
            # jezeli nie, przechodzimy do nastepnej pary
            else:
                current_clusters_pair[1] += 1
                # jezeli doszlismy do konca linii (patrz: trojkatna tablica dystansow), przechodzimy do nastepnej linii
                if current_clusters_pair[0] == current_clusters_pair[1]:
                    current_clusters_pair[0] += 1
                    current_clusters_pair[1] = 0
        MPIcomm.send(tmp_dist_list, 0)


# oblicza dystanse dla zadanego klastra
# distances     - trojkatan lista list dystansow
# clusters      - lista list wspolrzednych klastrow
# clusterIndex  - indeks klastra, dla ktorego maja zostac policzone dystanse
def countDistancesForNewCluster(distances, clusters, clusterIndex):
    if MPIrank == 0:
        # wysylamy klastry wszystkim wezlom
        if numberOfClusters > MPIsize - 1:
            loop_limits = [1, MPIsize]
        # jezeli klastrow jest mniej niz wezlow, czesc wezlow zwalniamy z pracy
        else:
            loop_limits = [1, numberOfClusters]

        # wysylamy wspolrzedne klastrow do wskazanej wyzej grupy wezlow
        for i in range(loop_limits[0], loop_limits[1]):
            MPIcomm.send(clusters, i)

        # zbieramy uzyskane wyniki i ustawiamy w odpowiednim miejscu w "distances"
        # najpierw uzupelniamy wiersz o indeksie "clusterIndex", a nastepnie kolumne o indeksie "clusterIndex"
        row = clusterIndex
        column = 0
        for i in range(loop_limits[0], loop_limits[1]):
            recived = MPIcomm.recv(source=i, tag=0)
            for j in range(0, len(recived)):
                # jezeli doszlismy do kolumny, ktorej wartosci trzeba zmienic, zatrzymujemy przesuwanie kolumny i
                # przesuwamy sie teraz po wierszach
                if column == clusterIndex:
                    row += 1
                distances[row][column] = recived[j]
                # jezeli nie doszlismy do kolumny, ktorej wartosci trzeba zmienic, przeskakujemy do nastepnej (
                # zmieniamy w ten sposob zadany wiersz)
                if column < clusterIndex:
                    column += 1

    elif MPIrank > 0:
        # odbieramy wyslane klastry
        if numberOfClusters - 1 >= MPIrank:  # jezeli klastrow jest mniej niz wezlow, zwalniamy wezly o wyzszych
            # indeksach
            recived_clusters = MPIcomm.recv(source=0, tag=0)
            tmp_dist_list = []

            # jezeli liczba klastrow jest mniejsza od ilosciwezlow, uruchomimy tyle wezlow ile jest klastrow
            number_of_workinging_nodes = MPIsize
            if numberOfClusters - 1 < MPIsize - 1:
                number_of_workinging_nodes = numberOfClusters

            # Jezeli zostala ostatnia para klastrow, poprostu obliczamy ich odleglosc i ja zwracamy
            if number_of_workinging_nodes == 2:
                dist = countDistance(recived_clusters[0], recived_clusters[1])
                tmp_dist_list.append(dist)
            else:
                # ustalamy jakie pary bedziemy liczyc w jakich wezlach
                limits = countLimitsForCountingDistances(0, numberOfClusters, MPIrank, number_of_workinging_nodes)
                second_cluster_index = limits[0]

                # obliczamy odleglosci na podstawie zadanego zestawu danych
                if limits[0] == limits[1]:
                    limits[1] += 1
                for i in range(limits[0], limits[1]):
                    # pomijamy wyliczanie zerowej odleglosci miedzy tym samym klastrem
                    if second_cluster_index == clusterIndex:
                        second_cluster_index += 1
                    # jezeli wyskoczylismy poza wskazane ograniczenia, wychodzimy w petli
                    if second_cluster_index == limits[1]:
                        break
                    dist = countDistance(recived_clusters[clusterIndex], recived_clusters[second_cluster_index])
                    tmp_dist_list.append(dist)
                    # przesuwamy indeks na kolejny klaster, dla ktorego chcemy wyliczyc odleglosc z tym zadanym przez
                    # "clusterIndex"
                    second_cluster_index += 1
            MPIcomm.send(tmp_dist_list, 0)


# oblicza srodek ciezkosci miedzy punkami
def countAveragePoint(p1, p2):
    result = []
    for i in range(0, len(p1)):
        avg = (p1[i] + p2[i]) / 2
        result.append(avg)
    return result


# usuwa zadane dystanse po sklejeniu klastrow
def removeAbsorbedClusterDistances(distances, cluster_index, number_of_clusters):
    for i in range(cluster_index + 1, number_of_clusters):
        del distances[i][cluster_index]
    del distances[cluster_index]


# skleja klastry o zadanych indeksach i usuwa zbedne dane z "clusters" i "distances"
def join2Clusters(distances, cl_with_lower_index, cl_with_higher_index, clusters, number_of_clusters):
    if cl_with_lower_index > cl_with_higher_index:
        tmp = cl_with_lower_index
        cl_with_lower_index = cl_with_higher_index
        cl_with_higher_index = tmp

    clusters[cl_with_lower_index] = countAveragePoint(clusters[cl_with_lower_index], clusters[cl_with_higher_index])
    del clusters[cl_with_higher_index]
    removeAbsorbedClusterDistances(distances, cl_with_higher_index, number_of_clusters)
    return [cl_with_lower_index, cl_with_higher_index]


# znajduje najlzeszy dystans z "distances"
def findLightestDistance(distances, number_of_clusters):
    if MPIrank == 0:
        number_of_distances = 0
        for i in range(1, number_of_clusters):
            number_of_distances += i

        # wysylamy pakiety dystansow do wlasciwych wezlow
        row = 1
        column = 0
        for i in range(1, MPIsize):
            tmp_list = []
            limits = count_limits_for_finding_the_lightest_distance(0, number_of_distances - 1, i, MPIsize)
            for j in range(limits[0], limits[1]):
                tmp_list.append(distances[row][column])
                column += 1
                if row == column:
                    row += 1
                    column = 0
            MPIcomm.send(tmp_list, i)

        # odbieramy pakiety i wybieramy najlepszy wynik
        best_dist = [0, 0, float("inf")]  # [nrWezla, nrOdleglosciNaOtrzymanejPrzezWezelLiscie, odleglosc]
        for i in range(1, MPIsize):
            recived = MPIcomm.recv()
            if recived[2] < best_dist[2]:
                best_dist = [recived[0], recived[1], recived[2]]

        # obliczamy dla podanego wyniku indeksy klastrow
        limits = count_limits_for_finding_the_lightest_distance(0, number_of_distances - 1, best_dist[0], MPIsize)
        position_in_distances = countCellPositionInDistancesTriangle(limits[0] + best_dist[1])

        for i in range(1, MPIsize):
            MPIcomm.send(position_in_distances, i)
        return position_in_distances

    elif MPIrank > 0:
        dist_list = MPIcomm.recv(source=0, tag=0)
        best_dist = [0, 0, float("inf")]
        for i in range(0, len(dist_list)):
            dist = dist_list[i]
            if best_dist[2] > dist:
                # zapisujemy: numer aktualnego wezla, pozycje najkrotszego dystansu na dostarczonej mu liscie,
                # wartosc dystansu
                best_dist[0] = MPIrank
                best_dist[1] = i
                best_dist[2] = dist

        MPIcomm.send(best_dist, 0)
        position_in_distances = MPIcomm.recv(source=0, tag=0)
        return position_in_distances  # kazdy z wezlow zapamietuje pozycje w dystansach najlepszego wyniku


# kazdy z wespol wypisuje przypisany mu indeks
print("Rank ", MPIrank)

# najpierw liczymy wzystkie mozliwe do wyliczenia dystanse
countAllDistances(clusters, numberOfPoints)

for i in range(1, numberOfPoints):
    # szukamy najkrotszego dystansu
    shortestDistance = findLightestDistance(distances, numberOfClusters)

    if MPIrank == 0:
        '''print "liczba klastrow", numberOfClusters
        for i in range (0, numberOfClusters):
            for j in range(0, i):
                print i, j, '{:1f}'.format(distances[i][j])
        print "\n"'''

        # laczymy dwa najbardziej zblizone do siebie klastry
        joins.append(join2Clusters(distances, shortestDistance[0], shortestDistance[1], clusters, numberOfClusters))

        # zapamietujemy indeks nowo utworzonego klastra (czyli jednego ze zlaczonych klastrow o nizszym indeksie)
        joinedClusterIndex = shortestDistance[1]
        if joinedClusterIndex > shortestDistance[0]:
            joinedClusterIndex = shortestDistance[0]

    # z po polaczeniu, zmiejszamy liczbe klastrow o 1
    numberOfClusters -= 1

    # jezeli jest wiecej niz jeden klaster, wyliczamy odleglosc powstalego ze zlaczenia klastra
    if numberOfClusters > 1:
        # wybieramy zgodnie z konwencja nizszy indeks
        if shortestDistance[0] < shortestDistance[1]:
            countDistancesForNewCluster(distances, clusters, shortestDistance[0])
        else:
            countDistancesForNewCluster(distances, clusters, shortestDistance[1])

if MPIrank == 0:
    print(joins)
