import pandas as pd
import numpy as np
from numpy.linalg import matrix_power
import logging

# Stała RI do obliczania współczynnika konsekwentności
RI = [0, 0, 0.52, 0.89, 1.11, 1.25, 1.35, 1.40, 1.45, 1.49]

# Funkcja do dzielenia stringów ułamkowych na wartości float
def divide_numbers(napis):
    napis = str(napis)
    if '/' in napis:
        return int(napis.split('/')[0]) / int(napis.split('/')[1])
    else:
        return float(napis)

# Funkcja obliczająca wartości własne i wektor priorytetów
def get_eig(df, eps=0.0001, max_iter=100):
    A = np.matrix(df)
    lambda_max = 0
    for i in range(max_iter):
        lambda_prev = lambda_max
        w_test = matrix_power(A, i + 1)
        w_test = w_test.sum(axis=1).tolist()
        w_test = [item for sublist in w_test for item in sublist]
        w_priority = [i / sum(w_test) for i in w_test]
        lambda_max = np.dot(A.sum(axis=0), w_priority).item()
        if abs(lambda_prev - lambda_max) < eps:
            return lambda_max, w_priority
    print("Algorithm did not converge")
    return lambda_max, w_priority

# Funkcja do obliczania współczynnika konsekwentności (CR)
def get_cr(l, n):
    ci = (l - n) / (n - 1)
    rci = RI[n-1] if n-1 < len(RI) else 0
    cr = ci / rci if rci != 0 else 0
    return cr

# Tworzenie macierzy porównań
def create_reciprocal_matrix(comparisons, options):
    n = len(options)
    matrix = np.ones((n, n))  # Tworzymy macierz kwadratową wypełnioną 1

    for comparison in comparisons:
        optionA = comparison['optionA']
        optionB = comparison['optionB']
        value = comparison['value']

        if value is None:
            continue  # Ignorujemy brakujące wartości

        indexA = options.index(optionA)
        indexB = options.index(optionB)

        matrix[indexA, indexB] = value['leftValue']
        matrix[indexB, indexA] = value['rightValue']

    return pd.DataFrame(matrix, index=options, columns=options)

# Funkcja do obliczania wyników klasycznego AHP
def calculate_classic_ahp(comparisons):
    criteria = set([comparison['criterion'] for comparison in comparisons])
    results = {}
    final_priority_vector = []
    total_cr = []

    for criterion in criteria:
        criterion_comparisons = [c for c in comparisons if c['criterion'] == criterion]
        options = list(set([c['optionA'] for c in criterion_comparisons] + [c['optionB'] for c in criterion_comparisons]))

        matrix = create_reciprocal_matrix(criterion_comparisons, options)
        lambda_max, w_priority = get_eig(matrix)
        cr = get_cr(lambda_max, len(matrix))

        results[criterion] = {
            'priority_vector': w_priority,
            'cr': cr
        }
        final_priority_vector.append(w_priority)
        total_cr.append(cr)

    avg_priority_vector = [sum(x) / len(x) for x in zip(*final_priority_vector)]
    avg_cr = sum(total_cr) / len(total_cr)

    # Uśrednione wyniki dla wszystkich kryteriów (opcjonalne, jeśli chcemy jeden wektor preferencji i jeden CR)
    avg_priority_vector = [sum(x) / len(x) for x in zip(*final_priority_vector)]
    avg_cr = sum(total_cr) / len(total_cr)
    return {
        "avg_priority_vector": avg_priority_vector,
        "avg_cr": avg_cr
    }

# Funkcja do obliczania środka masy dla rysunków
def calculate_center_of_mass(points):
    if not points:
        return None

    x_coords = [point['x'] for point in points]
    y_coords = [point['y'] for point in points]

    center_of_mass = {
        "x": sum(x_coords) / len(x_coords),
        "y": sum(y_coords) / len(y_coords)
    }
    return center_of_mass

# Funkcja do normalizacji punktów do przedziału -9 do 9
def normalize_point(value, original_min, original_max, target_min, target_max):
    return ((value - original_min) * (target_max - target_min)) / (original_max - original_min) + target_min

def normalize_drawing_to_range(center_of_mass_x, canvas_width, canvas_height):
    normalized_x = normalize_point(center_of_mass_x, 0, canvas_width, -9, 9)
    return normalized_x


# Funkcja do obliczania wyników AHP rysunkowego
# Funkcja do normalizacji X do przedziału (-9, 9)
def normalize_drawing_to_range(x_value, canvas_width):
    normalized_x = ((x_value - 0) * (9 - (-9))) / (canvas_width - 0) + (-9)
    # Dostosowanie wartości, aby była większa niż 1
    return max(abs(normalized_x), 1)

# Funkcja do obliczania wyników AHP rysunkowego
# Funkcja do obliczania wyników AHP rysunkowego
def calculate_drawing_ahp(comparisons, canvas_width=1000, canvas_height=500):
    criteria_set = set([comparison['criterion'] for comparison in comparisons])
    results = {}
    total_cr = []
    final_priority_vectors = []

    # Przetwarzamy każde kryterium osobno
    for criterion in criteria_set:
        criterion_comparisons = [comp for comp in comparisons if comp['criterion'] == criterion]

        # Zbieramy listę unikalnych opcji dla tego kryterium
        options = list(set([comp['optionA'] for comp in criterion_comparisons] + 
                           [comp['optionB'] for comp in criterion_comparisons]))

        # Tworzymy macierz wzajemnych porównań
        matrix = np.ones((len(options), len(options)))

        # Mapowanie opcji na indeksy
        option_to_index = {option: idx for idx, option in enumerate(options)}

        # Wypełniamy macierz wartościami z porównań
        for comparison in criterion_comparisons:
            points = comparison["value"]
            center_of_mass = calculate_center_of_mass(points)

            if center_of_mass:
                # Normalizujemy X do zakresu (-9, 9)
                normalized_value = normalize_drawing_to_range(center_of_mass['x'], canvas_width)
                logging.info(f"Porównanie kryterium '{criterion}' - Znormalizowana wartość (X): {normalized_value}")

                optionA = comparison['optionA']
                optionB = comparison['optionB']

                indexA = option_to_index[optionA]
                indexB = option_to_index[optionB]

                # Ustawiamy wartości preferencji w macierzy
                if normalized_value > 1:
                    matrix[indexA, indexB] = normalized_value
                    matrix[indexB, indexA] = 1 / normalized_value
                else:
                    matrix[indexA, indexB] = 1 / normalized_value
                    matrix[indexB, indexA] = normalized_value

        logging.info(f"Macierz recyprokalna dla kryterium '{criterion}':\n{matrix}")

        # Obliczamy wektor priorytetów i współczynnik konsekwentności
        lambda_max, w_priority = get_eig(matrix)
        cr = get_cr(lambda_max, len(matrix))

        # Zapisujemy wyniki dla każdego kryterium
        results[criterion] = {
            'priority_vector': w_priority,
            'cr': cr
        }

        final_priority_vectors.append(w_priority)
        total_cr.append(cr)

    # Uśrednione wartości dla wszystkich kryteriów
    avg_priority_vector = [sum(x) / len(x) for x in zip(*final_priority_vectors)]
    avg_cr = sum(total_cr) / len(total_cr)

    logging.info(f"Uśredniony wektor preferencji: {avg_priority_vector}")
    logging.info(f"Uśredniony współczynnik konsekwentności (CR): {avg_cr}")

    return {
        "avg_priority_vector": avg_priority_vector,
        "avg_cr": avg_cr
    }


# Funkcja do obliczania końcowego wektora preferencji
def calculate_final_preference(vectors, use_weighted_average=False, cr_values=None):
    n = len(vectors)
    if use_weighted_average and cr_values:
        weights = [1 / cr if cr > 0 else 0 for cr in cr_values]
        sum_weights = sum(weights)
        weighted_vectors = [[x * w for x in vec] for vec, w in zip(vectors, weights)]
        final_vector = [sum(x) / sum_weights for x in zip(*weighted_vectors)]
    else:
        final_vector = [sum(x) / n for x in zip(*vectors)]

    final_vector = [i / sum(final_vector) for i in final_vector]
    return final_vector
