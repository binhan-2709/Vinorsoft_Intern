# Bài 3: Roman to Integer
# Yêu cầu: Chuyển từ số La mã thành số nguyên
def romanToInt(s: str) -> int:
    roman_map: dict[str, int] = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }
    
    total = 0
    
    for i in range(len(s) - 1):
        if roman_map[s[i]] < roman_map[s[i+1]]:
            total -= roman_map[s[i]]
        else:
            total += roman_map[s[i]]
    total += roman_map[s[-1]]
    
    return total

print("Test 1 (III):", romanToInt("III"))      
print("Test 2 (LVIII):", romanToInt("LVIII"))   
print("Test 3 (MCMXCIV):", romanToInt("MCMXCIV")) 