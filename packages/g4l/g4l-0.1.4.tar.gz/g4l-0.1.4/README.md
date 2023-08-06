# g4l

>- gpio for linux (tested with jetson tx2, nano)
>- link : <https://gitlab.com/telelian/peripheral-library/g4l>



## Usage

### class 

- Gpio(num)
    - parameter
        - num : gpio number

### methods

- Gpio.direction(dir)
    - parameters
        - dir : pin's direction ( Gpio.IN, Gpio.OUT )

- Gpio.edge(edge)
    - parameters
        - edge : interrupt edge (Gpio.NONE, Gpio.RISING, Gpio.FALLING, Gpio.BOTH)

- Gpio.input()
    - returns
        - input value

- Gpio.output(value)
    - parameters
        - value : output value

- Gpio.setisr(isr)
    - parameters
        - isr : interrupt service routines's callback function
        
### example

#### input interrupt
~~~python
from time import sleep
from g4l import Gpio

print('g4l example')
gpio = Gpio(100)
gpio.direction(Gpio.IN)
gpio.edge(Gpio.RISING)
gpio.setisr(lambda:print('gpio isr'))
    
print('loop start - toggle gpio')
cnt = 0
while True:
    print(f'loop {cnt}')
    cnt += 1
    sleep(5)
~~~