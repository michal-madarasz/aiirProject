import math
import numpy as np
from mpi4py import MPI
import csv
import sys
import os

# import sklearn.cluseter.hierarchy as sch

# konwencja:
# przy zmiejszaniu tablicy klastrow, usredniony wynik zapisujemy w komorkach o nizszym indeksie, a te o wyzszym usuwamy
# wezel o indeksie 0 to master
# przy laczeniu dwoch klastrow, nowoutworzony klaster otwrzymuje indeks po rodzicu, ktorego indeks byl nizszy
# pierwszy i ostatni komputer warto zeby byly najszybsze:
    # pierwszy ze wzgledu na to, ze w kilku miejscach cala reszta musi czekac na niego,
    #  drugi ze wzg;edu na to, ze zazwyczaj musi wyliczyc o 1-2 odleglosci wiecej


MPIcomm = MPI.COMM_WORLD    # zmienna sluzaca do wywolywania funkcji MPI; laczy wszystkie wezly
MPIrank = MPIcomm.rank      # zmienna przechowujaca indeks danego wezla
MPIsize = MPIcomm.size      # zmienna przechowujaca liczbe wszystkich wezlow

filename_load = sys.argv[1]
filename_save = sys.argv[2]

# nazawa input-pliku data.csv
clusters_str = list(csv.reader(open(filename_load, 'r')))
clusters = []
clusters = [[0 for i in range(len(clusters_str[j]))] for j in range(len(clusters_str))]

for j in range(len(clusters_str)):
    for i in range(len(clusters_str[j])):
        clusters[j][i] = float(clusters_str[j][i])

numberOfPoints = len(clusters)
#clusters = [[0,2], [2,4], [3,5], [4,6], [5,7],                  # lista przechowujaca wspolrzedne wszystkich klastrow ( zmienia sie z kazda iteracja )
    # [1.5, 1.8],[2.5, 2.8],[3.5, 3.8],[4.5, 4.8],[5.5, 5.8],
    # [5, 8],[6, 9],[7, 1],[8, 2],[9, 3],
    # [8, 8], [9, 9], [1, 1], [2, 2],[3, 3],
    # [1, 0.6],[2, 1.6],[3, 2.6],[4, 3.6],[5, 4.6],
    # [9, 11],[1, 2],[3, 4],[5, 6],[7, 8]]

#numberOfPoints = 10
#clusters =  [[0,1], [1,3], [2,6], [3,10], [4,15],
#            [5,21], [6,28], [7,36], [8,45], [9,55]]

#numberOfPoints = 5
#clusters = [[4,15], [3,10], [2,6], [1,3], [0,1]]


numberOfClusters = numberOfPoints           # wskazuje aktualna liczbe klastrow

distances = []                              # lista list dystansow miedzy klastrami
                                            # Jest w ksztalcie trojkata: "i"-ty wiersz posiada "i" rekordow
                                            # przyklad dla 4 klastrow ("x" oznacza jakas wartosc)
                                            #   0 1 2 3
                                            # 0
                                            # 1 x
                                            # 2 x x
                                            # 3 x x x

for i in range(0, numberOfClusters):        # inicjalizacja listy list dystansow zerami
    tmp_list = []
    for j in range(0, i):
        tmp_list.append(0)
    distances.append(tmp_list)


joins = []                                  # lista kolejnych zlaczen; wynik dzialania programu
translationList = []                        # lista tlumaczaca numer klastra na numer, ktory bedzie interpretowany przez rysownika dendrogramu
                                            # dendrogram zaklada, ze kazdy nowo powstaly klaster otrzymuje indeks n+1, gdzie n to indeks ostatniego zapisanego klastra
lastClasterDendroIndex = numberOfPoints - 1 # indeks klastra o najwyzszym indeksie wedlug indeksowania dla dendrogramu
shortestDistance = [0, 0, float('inf')]     # najkrotszy dystans zapamietany przez wszystkie wezly


# Wskazuje podzial przeszukiwanej listy dystansow dla wezlow-robotnikow
# lower - dolna granica, indeks pierwszego dystansu na liscie ( powinien byc zawsze rowny 0 )
# upper - gorna granica, indeks gornego dystansu na liscie ( powinien byc zawsze numberOfDistances - 1 )
# nodeNo - numer wezla ( uwaga: wezel 0 to master, wszystkie inne zajmuja sie wyliczaniem i wlasnie ich indeksy podajemy jako argument )
# nodesAmout - liczba wszystkich wezlow ( lacznie z masterem )
def countLimitsForFindingTheLightestDistance(lower, upper, nodeNo, nodesAmount):
    lowerLimit = (nodeNo-1) * (upper - lower) / (nodesAmount - 1)       # nodeAmount - 1 zeby nie wliczac mastera
    upperLimit = (nodeNo * (upper - lower) / (nodesAmount - 1))         #
    if nodeNo + 1 == nodesAmount:                                       # zeby przeliczyc caly zbior, ostani wezel musi policzyc o jeden element wiecej
        upperLimit += 1
    return [int(math.floor(lowerLimit)), int(math.floor(upperLimit))]

# Wskazuje przedzial listy wspolrzednych klastrow, dla ktorych wezly-robotnicy beda wyliczac odleglosc od nowoutworzonego klastra
# lower - dolna granica, indeks pierwszego dystansu na liscie ( powinien byc zawsze rowny 0 )
# upper - gorna granica, indeks gornego dystansu na liscie ( powinien byc zawsze numberOfDistances - 1 )
# nodeNo - numer wezla ( uwaga: wezel 0 to master, wszystkie inne zajmuja sie wyliczaniem i wlasnie ich indeksy podajemy jako argument )
# nodesAmout - liczba wszystkich wezlow ( lacznie z masterem )
def countLimitsForCountingDistances(lower, upper, nodeNo, nodesAmount):
    lowerLimit = (nodeNo-1) * (upper - lower) / (nodesAmount - 1)       # nodeAmount - 1 zeby nie wliczac mastera
    upperLimit = (nodeNo * (upper - lower) / (nodesAmount - 1))
    return [int(lowerLimit), int(upperLimit)]

# Wskazuje przedzial listy wspolrzednych klastrow, dla ktorych wezly-robotnicy beda wyliczac odleglosc od nowoutworzonego klastra za pierwszym razem
# lower - dolna granica, indeks pierwszego dystansu na liscie ( powinien byc zawsze rowny 0 )
# upper - gorna granica, indeks gornego dystansu na liscie ( powinien byc zawsze numberOfDistances - 1 )
# nodeNo - numer wezla ( uwaga: wezel 0 to master, wszystkie inne zajmuja sie wyliczaniem i wlasnie ich indeksy podajemy jako argument )
# nodesAmout - liczba wszystkich wezlow ( lacznie z masterem )
def countLimitsForFirstCountingDistances(lower, upper, nodeNo, nodesAmount):
    lowerLimit = (nodeNo-1) * (upper - lower) / (nodesAmount - 1)       # nodeAmount - 1 zeby nie wliczac mastera
    upperLimit = (nodeNo * (upper - lower) / (nodesAmount - 1)) - 1     # - 1 zeby zbiory granice na siebie nie nachodzily
    if nodeNo + 1 == nodesAmount:                                       # zeby przeliczyc caly zbior, ostani wezel musi policzyc o jeden element wiecej
        upperLimit += 1
    return [int(lowerLimit), int(upperLimit)]

# wylicza pozycje komorki w trojkacie dystansow na podstawie jej indeksu;
# indexOfData - indeks wylicza sie tak, jakby dystansy byly dane byly zapisane w jedno wymiarowej liscie
def countCellPositionInDistancesTriangle(indexOfData):
    row = 1
    while row <= indexOfData:
        indexOfData -= row
        row += 1
    column = indexOfData
    return [row, column]

# liczy dystans miedzy dwoma punktami w przestrzeni o dowolnej liczbie dystansow
# p1, p2 - wspolrzedne punktow (kolejnosc podanych argumentow jest bez znaczenia
def countDistance(p1, p2):
    result = 0
    for i in range(0, len(p1)):
        result+=(p1[i]-p2[i])**2
    result = np.math.sqrt(result)
    return result

# wylicza dystasy miedzy kazda mozliwa para klastrow
# clusters - wskazuje wspolrzedne klastrow
# numberOfClusters - wskazuje liczbe klastrow
def countAllDistances(clusters, numberOfClusters):
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
        recivedClusters = MPIcomm.recv(source=0, tag=0)
        tmp_dist_list = []

        # ustalamy przedzialy dystansow do policzenia przez wezel-robotnika
        numberOfDistancesToCount = 0
        for i in range(1, numberOfClusters):
            numberOfDistancesToCount += i                                                                   # liczymy ile dystansow jest calkowicie do polaczenia
        limits = countLimitsForFirstCountingDistances(0, numberOfDistancesToCount - 1, MPIrank, MPIsize)    # i bierzemy odpowiedni zestaw dla danego wezla
        currentClustersPair = countCellPositionInDistancesTriangle(limits[0])                               # poruszamy sie po klastrze przy pomocy wskazanej pary
        endClustersPair = countCellPositionInDistancesTriangle(limits[1])                                   # konczymy obliczanie gdy obliczymy odleglosc dla ostatniej pary

        # obliczamy odleglosci na podstawie zadanego zestawu danych
        while True:
            dist = countDistance(recivedClusters[currentClustersPair[0]], recivedClusters[currentClustersPair[1]])
            tmp_dist_list.append(dist)
            # jezeli obliczylismy wartosci dla ostatniej pary, wychodzimy z petli
            if currentClustersPair[0] == endClustersPair[0] and currentClustersPair[1] == endClustersPair[1]:
                break
            # jezeli nie, przechodzimy do nastepnej pary
            else:
                currentClustersPair[1] += 1
                # jezeli doszlismy do konca linii (patrz: trojkatna tablica dystansow), przechodzimy do nastepnej linii
                if currentClustersPair[0] == currentClustersPair[1]:
                    currentClustersPair[0] += 1
                    currentClustersPair[1] = 0
        MPIcomm.send(tmp_dist_list, 0)

# oblicza dystanse dla zadanego klastra
# distances     - trojkatan lista list dystansow
# clusters      - lista list wspolrzednych klastrow
# clusterIndex  - indeks klastra, dla ktorego maja zostac policzone dystanse
def countDistancesForNewCluster(distances, clusters, clusterIndex):
    if MPIrank == 0:
        # wysylamy klastry wszystkim wezlom
        loopLimits = []
        if(numberOfClusters > MPIsize-1):
            loopLimits = [1, MPIsize]
        # jezeli klastrow jest mniej niz wezlow, czesc wezlow zwalniamy z pracy
        else:
            loopLimits = [1, numberOfClusters]

        # wysylamy wspolrzedne klastrow do wskazanej wyzej grupy wezlow
        for i in range(loopLimits[0], loopLimits[1]):
            MPIcomm.send(clusters, i)

        # zbieramy uzyskane wyniki i ustawiamy w odpowiednim miejscu w "distances"
        # najpierw uzupelniamy wiersz o indeksie "clusterIndex", a nastepnie kolumne o indeksie "clusterIndex"
        row = clusterIndex
        column = 0
        for i in range(loopLimits[0], loopLimits[1]):
            recived = MPIcomm.recv(source=i, tag=0)
            for j in range(0, len(recived)):
                # jezeli doszlismy do kolumny, ktorej wartosci trzeba zmienic, zatrzymujemy przesuwanie kolumny i przesuwamy sie teraz po wierszach
                if column == clusterIndex:
                    row += 1
                distances[row][column] = recived[j]
                # jezeli nie doszlismy do kolumny, ktorej wartosci trzeba zmienic, przeskakujemy do nastepnej (zmieniamy w ten sposob zadany wiersz)
                if column < clusterIndex:
                    column += 1

    elif MPIrank > 0:
        # odbieramy wyslane klastry
        if numberOfClusters - 1 >= MPIrank:  # jezeli klastrow jest mniej niz wezlow, zwalniamy wezly o wyzszych indeksach
            recivedClusters = MPIcomm.recv(source=0, tag=0)
            tmp_dist_list = []

            # jezeli liczba klastrow jest mniejsza od ilosciwezlow, uruchomimy tyle wezlow ile jest klastrow
            numberOfWorkingingNodes = MPIsize
            if numberOfClusters - 1 < MPIsize - 1:
                numberOfWorkingingNodes = numberOfClusters

            # Jezeli zostala ostatnia para klastrow, poprostu obliczamy ich odleglosc i ja zwracamy
            if numberOfWorkingingNodes == 2:
                dist = countDistance(recivedClusters[0], recivedClusters[1])
                tmp_dist_list.append(dist)
            else:
                # ustalamy jakie pary bedziemy liczyc w jakich wezlach
                limits = countLimitsForCountingDistances(0, numberOfClusters, MPIrank, numberOfWorkingingNodes)
                secondClasterIndex = limits[0]

                # obliczamy odleglosci na podstawie zadanego zestawu danych
                if limits[0] == limits[1]:
                    limits[1] += 1
                for i in range(limits[0], limits[1]):
                    # pomijamy wyliczanie zerowej odleglosci miedzy tym samym klastrem
                    if secondClasterIndex == clusterIndex:
                        secondClasterIndex += 1
                    # jezeli wyskoczylismy poza wskazane ograniczenia, wychodzimy w petli
                    if secondClasterIndex == limits[1]:
                        break
                    dist = countDistance(recivedClusters[clusterIndex], recivedClusters[secondClasterIndex])
                    tmp_dist_list.append(dist)
                    # przesuwamy indeks na kolejny klaster, dla ktorego chcemy wyliczyc odleglosc z tym zadanym przez "clusterIndex"
                    secondClasterIndex += 1
            MPIcomm.send(tmp_dist_list, 0)

# oblicza srodek ciezkosci miedzy punkami
def countAveragePoint(p1, p2):
    result = []
    for i in range(0, len(p1)):
        avg = (p1[i]+p2[i])/2
        result.append(avg)
    return result

# usuwa zadane dystanse po sklejeniu klastrow
def removeAbsorbedClusterDistances(distances, clasterIndex, numberOfClusters):
    for i in range(clasterIndex + 1, numberOfClusters):
        del distances[i][clasterIndex]
    del distances[clasterIndex]

# skleja klastry o zadanych indeksach i usuwa zbedne dane z "clusters" i "distances"
def join2Clusters(distances, clWithLowerIndex, clWithHigherIndex, clusters, numberOfClusters):
    if clWithLowerIndex > clWithHigherIndex:
        tmp = clWithLowerIndex
        clWithLowerIndex = clWithHigherIndex
        clWithHigherIndex = tmp

    clusters[clWithLowerIndex] = countAveragePoint(clusters[clWithLowerIndex], clusters[clWithHigherIndex])
    del clusters[clWithHigherIndex]
    removeAbsorbedClusterDistances(distances, clWithHigherIndex, numberOfClusters)
    return [clWithLowerIndex, clWithHigherIndex]

# znajduje najlzeszy dystans z "distances"
def findLightestDistance(distances, numberOfClusters):
    if MPIrank == 0:
        numberOfDistances = 0
        for i in range(1, numberOfClusters):
            numberOfDistances += i

        # wysylamy pakiety dystansow do wlasciwych wezlow
        row = 1
        column = 0
        for i in range(1, MPIsize):
            tmp_list = []
            limits = countLimitsForFindingTheLightestDistance(0, numberOfDistances - 1, i, MPIsize)
            for j in range(limits[0], limits[1]):
                tmp_list.append(distances[row][column])
                column += 1
                if row == column:
                    row += 1
                    column = 0
            MPIcomm.send(tmp_list, i)

        # odbieramy pakiety i wybieramy najlepszy wynik
        best_dist = [0, 0, float("inf")]    # [nrWezla, nrOdleglosciNaOtrzymanejPrzezWezelLiscie, odleglosc]
        for i in range(1, MPIsize):
            recived = MPIcomm.recv()
            if recived[2] < best_dist[2]:
                best_dist = [recived[0], recived[1], recived[2]]

        # obliczamy dla podanego wyniku indeksy klastrow
        limits = countLimitsForFindingTheLightestDistance(0, numberOfDistances - 1, best_dist[0], MPIsize)
        positionInDistances = countCellPositionInDistancesTriangle(limits[0] + best_dist[1])

        for i in range(1, MPIsize):
            MPIcomm.send(positionInDistances, i)
        return positionInDistances

    elif MPIrank > 0:
        dist_list = MPIcomm.recv(source=0, tag=0)
        best_dist = [0, 0, float("inf")]
        for i in range(0, len(dist_list)):
                dist = dist_list[i]
                if best_dist[2] > dist:
                    # zapisujemy: numer aktualnego wezla, pozycje najkrotszego dystansu na dostarczonej mu liscie, wartosc dystansu
                    best_dist[0] = MPIrank
                    best_dist[1] = i
                    best_dist[2] = dist

        MPIcomm.send(best_dist, 0)
        positionInDistances = MPIcomm.recv(source=0, tag=0)
        return positionInDistances          # kazdy z wezlow zapamietuje pozycje w dystansach najlepszego wyniku

def appendToJoinList(joinedClusters):
    firstIndex = translationList[joinedClusters[0]]
    secondIndex = translationList[joinedClusters[1]]
    joins.append([firstIndex, secondIndex, len(joins)+1, 2])        # arg[0] - indeks klastra o nizszym indeksie
                                                                    # arg[1] - indeks klastra o wyzszym indeksie
                                                                    # arg[2] - wysokosc zlaczenia
                                                                    # arg[3] - ile klastrow laczymy

    # usuwamy zlaczany klaster o wyzszym indeksie z listy tlumaczen na indeksy dla dendrogramu
    del translationList[joinedClusters[1]] #= translationList[:joinedClusters[1]] + translationList[joinedClusters[1]+1:]

    translationList[joinedClusters[0]] = lastClasterDendroIndex + 1


# kazdy z wespol wypisuje przypisany mu indeks
print("Rank ", MPIrank)

# najpierw liczymy wzystkie mozliwe do wyliczenia dystanse
countAllDistances(clusters, numberOfPoints)

if MPIrank == 0:
    for i in range(0, numberOfPoints):
        translationList.append(i)

for i in range(1, numberOfPoints):
    # szukamy najkrotszego dystansu
    shortestDistance = findLightestDistance(distances, numberOfClusters)

    if MPIrank == 0:

        # laczymy dwa najbardziej zblizone do siebie klastry i inkrementujemy indeks ostatniego wpisanego do listy polaczen klastra
        appendToJoinList(join2Clusters(distances, shortestDistance[0], shortestDistance[1], clusters, numberOfClusters))
        lastClasterDendroIndex += 1

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

# if MPIrank == 0:
#     print(translationList)
#     print("\n")
#     print(joins)

# zapisujemy do pliku
joinsOutput = open(filename_save, "a")
joinsOutput.write("\n".join(map(str, joins)))
joinsOutput.close()