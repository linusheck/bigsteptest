def sum_numbers_in_file(file_path):
    total_sum = 0
    with open(file_path, 'r') as file:
        for line in file:
            try:
                number = float(line.split(" ")[-2])
                total_sum += number
            except ValueError:
                print(f"Skipping non-numeric line: {line.strip()}")
    return total_sum

if __name__ == "__main__":
    file_path = 'iterations_robust.txt'
    result = sum_numbers_in_file(file_path)
    print(f"The total sum of numbers in the file is: {result}")