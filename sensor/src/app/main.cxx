#include <iostream>
 
int main() {
  std::cout << "GCC Version: " << __GNUC__ << "." << __GNUC_MINOR__ << "." << __GNUC_PATCHLEVEL__ << std::endl;
  std::cout << "__cplusplus Value: " << __cplusplus << std::endl;

  bool correct_version{false};

  // Map __cplusplus to standard name
  if (__cplusplus >= 202302L) std::cout << "C++23 or later" << std::endl;
  else if (__cplusplus >= 202002L) {
    std::cout << "C++20" << std::endl;
    correct_version = true;
	}
  else if (__cplusplus >= 201703L) std::cout << "C++17" << std::endl;
  else if (__cplusplus >= 201402L) std::cout << "C++14" << std::endl;
  else if (__cplusplus >= 201103L) std::cout << "C++11" << std::endl;
  else std::cout << "C++98 or older" << std::endl;
   
  if (!correct_version) {
    std::cout << "\nIncorrect C++ Standard Used!\n";
    return -1;
  }

    

  return 0;
}
