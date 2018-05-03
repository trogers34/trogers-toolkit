//
//  main.cpp
//  cpp-trogers
//
//  Created by Timothy Rogers on 5/2/18.
//  Copyright © 2018 Timothy Rogers. All rights reserved.
//

#include <iostream>
#include "MyTest.h"

void doStackStuff (MyTest& myTest)
{
    myTest.printEvenMoreStuff();
}

void doWeakStuff ( std::weak_ptr<MyTest> ptr)
{
    std::shared_ptr<MyTest> sharedPtr = ptr.lock();
    sharedPtr->printMoreStuff();
}

int main(int argc, const char * argv[]) {
    // insert code here...
    std::cout << "Hello, World!\n";
    
    std::unique_ptr<MyTest> myPtr1(new MyTest);
    
    myPtr1->printStuff();
    
    std::unique_ptr<MyTest> myPtr2;
    myPtr2 = std::move(myPtr1);
    
    if (NULL == myPtr1.get())
    {
        std::cout << "Found null as expected" << std::endl;
    }
    
    std::shared_ptr<MyTest> myPtr3(new MyTest);
    doWeakStuff(myPtr3);
    
    doStackStuff(*myPtr3);
    return 0;
}
