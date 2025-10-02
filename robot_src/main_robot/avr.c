//#define F_CPU 16000000UL
//#include <avr/io.h>
//
//int main(void)
//{
//DDRA = 0XFF;
//DDRB = 0XFF;
//DDRC = 0XFF;
//DDRD = 0XFF;
//DDRE = 0XFF;
//DDRF = 0XFF;
//DDRG = 0XFF;
//
//
//PORTA = 0xff;
//PORTB = 0xff;
//PORTC = 0xff;
//PORTD = 0xff;
//PORTE = 0xff;
//PORTF = 0xff;
//PORTG = 0xff;
//}

// 모터 구동부 소스
#define F_CPU 16000000UL
#include <avr/io.h>
#include <util/delay.h>

void serial_Init(unsigned long boud)
{
	unsigned short ubrr;						//보레이트 설정
	ubrr=(unsigned short)(F_CPU/(16*boud)-1);	//UBRRn 비동기 표준모드 계산식 클록 위에 설정
	UBRR0H = (unsigned char)(ubrr>>8);			//보레이트 레지스터 상위 4비트
	UBRR0L = (unsigned char) ubrr;			//보레이트 레지스터 하위 8비트
	
	UCSR0B = (1<<RXEN0) | (1<<TXEN0);			//RX수신부 가능,TX 송신부 가능
	UCSR0C = (3<<UCSZ00);						//비동기 모드, 패리티 불능, 정지 1비트, 문자크기 8비트
}

int main(void)
{
	char command;
	int i=0;
	float duty = 250;
	float duty_left = duty;
	float duty_right = duty;
	
	char flag = 0;
	char flag2 = 0;
	char flag3 = 0;
	char flag4 = 0;
	int linear = 4000; // 리니어 다 펴졌을 때
	DDRB = 0xff;
	DDRD = 0xff;
	DDRE = 0xfa;
	DDRA = 0xff;
	
	// 8비트 타이머/카운터 0 (모터 드라이버 1)
	TCCR0 = (1<<WGM01)|(1<<WGM00)|(2<<COM00);
	TCCR0 |= (0x02<<CS00);
	
	// 8비트 타이머/카운터 2 (모터 드라이버 2)
	TCCR2 = (1<<WGM21)|(1<<WGM20)|(2<<COM20);
	TCCR2 |= (0x02<<CS20);

	
	TCCR1A = 0xA2; // 0b 101010
	TCCR1B = 0x1A; // 분주비 8비트
	
	TCCR3A = 0xAA; //0b 101010
	TCCR3B = 0x1A; // 분주비 8비트
	
	ICR1 = 40000;
	ICR3 = 40000;
	
	serial_Init(9600);
	OCR1A = linear;
	OCR1B = 2400; // 문이 열려 있을 떄
	OCR3C = 4500; // 문이 열려 있을 때
	
	OCR0 = duty; // 왼쪽 바퀴 모터 드라이버?
	OCR2 = duty; // 오른쪽 바퀴 모터 드라이버?
	OCR3A = 2400;
	OCR3B = 4500;
	
	PORTA = 0x01;
	
	while (1)
	{//OCR1B 9번 OCR3C 10번
		while(!(UCSR0A & (1<<RXC))==0x00){
			command = UDR0;
			//  1001
			if(command == 'w'){
				PORTD = 0b01101001; 
				
				duty_right =250;
				duty_left =250;
			}
			else if(command == 's') PORTD = 0b10010110;
			else if(command == 'd') PORTD = 0b01011010;
			else if(command == 'a') PORTD = 0b10100101;
			else if(command == 'c') PORTD = 0x00;
			
			////////////////// 전진 좌회전 //////////////////////////
			else if(command == 'q'){
				PORTD = 0b01101001;
				duty_left -= 2.5;
				if(duty_left<=0) duty_left =0;
			}
			////////////////// 전진 우회전 //////////////////////////
			else if(command == 'e'){
				PORTD = 0b01101001;
				duty_right -= 2.5;
				if(duty_right<=0) duty_right =0;
			}
			////////////////// 후진 좌회전 //////////////////////////
			else if(command == 'z'){
				PORTD = 0b01011010;
				duty_left -= 2.5;
				if(duty_left<=0) duty_left =0;
			}
			////////////////// 후진 우회전 //////////////////////////
			else if(command == 'x'){
				PORTD = 0b01011010;
				duty_right -= 2.5;
				if(duty_right<=0) duty_right =0;
			}
			////////////////// 제자리 좌회전 ////////////////////////
			else if(command == 'r'){
				PORTD = 0b10101010;
			}
			////////////////// 제자리 우회전 ////////////////////////
			else if(command == 't'){
				PORTD = 0b01010101;
			}
			//else if(command == '+'){
			//duty += 12.5;
			//if(duty >= 250) duty = 250;
			//duty_left = duty;
			//duty_right = duty;
			//}
			//
			//else if(command == '-'){
			//duty -= 12.5;
			//if(duty <= 0) duty = 0;
			//duty_left = duty;
			//duty_right = duty;
			//
			//}
			/////////////////////// 리니어 //////////////////////////////////
			else if(command == 'h'){
				if (flag == 0){
					//for(i=0; i<2000;i++){ // 2000 : 리니어 접혔을 때
						//OCR1A -= 1;
						//_delay_ms(1);
					//}
					OCR1A = 2000;
					flag = 1;
				}
				else if(flag == 1){
					//for(i=0; i<2000;i++){ // 4000 : 리니어 최대로 펴졌을 때
						//OCR1A += 1;
						//_delay_ms(1);
					//}
					OCR1A = 4000;
					flag = 0;
				}
			}
			///////////////////// 문짝 서보 //////////////////////////////////
			else if(command == 'j'){
				if (flag2 == 0){ // 펴져 있을 때
					for(i=0;i<2000;i++){
						OCR1B += 1;
						OCR3C -= 1;
						_delay_ms(1);
					}
					flag2 = 1;
				}
				else if (flag2 == 1){ // 접혀 있을때
					for(i=0;i<2000;i++){
						OCR1B -= 1;
						OCR3C += 1;
						_delay_ms(1);
					}
					flag2 = 0;
				}
			}
			
			/////////////////// 소화기 서보//////////////////////////////
			else if(command == 'k'){
				if (flag3 == 0){
					for(i=0;i<1300;i++){
						OCR3A += 1;
						OCR3B-=1;
						_delay_ms(1);
					}
					flag3 = 1;
				}
				
				else if (flag3 == 1){
					for(i=0;i<1300;i++){
						OCR3A -= 1;
						OCR3B += 1;
						_delay_ms(1);
					}
					flag3 = 0;
				}
			}
			//////////////////// 전방 LED //////////////////////////////
			else if(command == 'l'){
				if (flag4 == 0){
					PORTA = 0x00;
					flag4 = 1;
				}
				
				else if (flag4 == 1){
					PORTA = 0x01;
					flag4 = 0;
				}
			}
			
			else if (command == 'r'){duty_left = 250; duty_right = 250;}
			else PORTD = 0x00;
			
			OCR0 = duty_left;
			OCR2 = duty_right;
		}
	}
}
