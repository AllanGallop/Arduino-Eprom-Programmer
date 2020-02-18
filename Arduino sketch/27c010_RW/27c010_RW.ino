//FIXME
const int programPin=23;
const int readPin=37;
const int enablePin=41;
const int VppHI = 4;
const int VppLO = 3;
const unsigned long romSize=1024*1024;
int adrPins[17]={42,//eprom A0
                  40,//eprom A1
                  38,//eprom A2
                  36,//eprom A3
                  34,//eprom A4
                  32,//eprom A5
                  30,//eprom A6
                  28,//eprom A7
                  31,//eprom A8
                  33,//eprom A9
                  39,//eprom A10
                  35,//eprom A11
                  26,//eprom A12
                  29,//eprom A13
                  27,//eprom A14
                  24,//eprom A15
                  22,//eprom A18
                  };
char dataPins[8]={44,46,48,51,49,47,45,43};
byte inByte=0;
unsigned int secH=0,secL=0;

void setup() {
  pinMode(programPin,OUTPUT);
  pinMode(readPin,OUTPUT);
  pinMode(enablePin,OUTPUT);
  pinMode(VppHI, OUTPUT);
  pinMode(VppLO, OUTPUT);
  for(int i=0;i<20;i++){
    pinMode(adrPins[i],OUTPUT);
  }
  digitalWrite(programPin,HIGH); //PGM Low to write, high to read
  digitalWrite(readPin,HIGH);    //OE Low to write, high to read
  digitalWrite(enablePin,LOW);   //CR Low to enable
  digitalWrite(VppHI,LOW);       //Vpp 13v
  digitalWrite(VppLO,HIGH);      //Vpp 5v
  Serial.begin(250000);
  delay(1000);

}
int index=0;
void loop() {
  if(Serial.available()){
    inByte=Serial.read();
    if(inByte==0x55){
      while(Serial.available()==0);
      inByte=Serial.read();
      switch(inByte){
        case 'w':
          programMode();
          while(Serial.available()<2);
          secH=Serial.read();
          secL=Serial.read();
          writeSector(secH,secL);
          break;
        case 'r':
          readMode();
          readROM();
          break;
      }
    }
  }
}


//low level functions, direct hardware pins
void programMode(){
  //data as output
  for(int i=0;i<8;i++){
    pinMode(dataPins[i],OUTPUT);
  }
  digitalWrite(readPin,HIGH);
  digitalWrite(programPin,HIGH);
}
void readMode(){
  //data as input
  for(int i=0;i<8;i++){
    pinMode(dataPins[i],INPUT);
  }
  digitalWrite(VppHI,LOW);
  digitalWrite(VppLO,HIGH);  //Vpp 5v
  digitalWrite(programPin,HIGH);
  digitalWrite(readPin,LOW);

}
void setAddress(uint32_t Addr){
    for(int i=0;i<8;i++){
      digitalWrite(adrPins[i],Addr&(1<<i));
    }
    Addr=Addr>>8;
    for(int i=0;i<8;i++){
      digitalWrite(adrPins[i+8],Addr&(1<<i));
    }
    Addr=Addr>>8;
    for(int i=0;i<4;i++){
      digitalWrite(adrPins[i+16],Addr&(1<<i));
    }
}
byte readByte(unsigned long adr){
    byte data;
    setAddress(adr);
    digitalWrite(readPin,LOW);
    delayMicroseconds(1);
    for(int i=7;i>=0;i--){
        data=data<<1;
        data|=digitalRead(dataPins[i])&1;
    }
    digitalWrite(readPin,HIGH);
    return data;
}
void setData(char Data){
  for(int i=0;i<8;i++){
      digitalWrite(dataPins[i],Data&(1<<i));
  }
}
void programByte(byte Data){
  digitalWrite(VppLO,LOW);
  digitalWrite(VppHI,HIGH);  //Vpp 12v
  delayMicroseconds(10);
  setData(Data);
  
  //PGM pulse
  delayMicroseconds(100);
  digitalWrite(programPin,LOW);
  delayMicroseconds(200);
  digitalWrite(programPin,HIGH);

  //Verify Pulse
  delayMicroseconds(10);
  digitalWrite(readPin,LOW);
  delayMicroseconds(10);
  digitalWrite(readPin,HIGH);
  
  //PGM Over pulse  
  delayMicroseconds(100);
  digitalWrite(programPin,LOW);
  delayMicroseconds(400);
  digitalWrite(programPin,HIGH);

  delayMicroseconds(10);
  digitalWrite(VppHI,LOW);
  digitalWrite(VppLO,HIGH);  //Vpp 5v
}

void writeSector(unsigned char sectorH,unsigned char sectorL){
  byte dataBuffer[128];
  unsigned long address=0;
  byte CHK=sectorH,CHKreceived;
  CHK^=sectorL;

  address=sectorH;
  address=(address<<8)|sectorL;
  address*=128;

  for(int i=0;i<128;i++){
        while(Serial.available()==0);
        dataBuffer[i]=Serial.read();
        CHK ^= dataBuffer[i];
  }
  while(Serial.available()==0);
  CHKreceived=Serial.read();
  programMode();
  //only program the bytes if the checksum is equal to the one received
 
    for (int i = 0; i < 128; i++){
      setAddress(address++);
      programByte(dataBuffer[i]);
    }
  Serial.write(CHK);
  readMode();
}
int readROM(){
  unsigned long num=1024*1024;
  unsigned long address;
  byte data,checksum=0;
  address=0;
  //read mode
  readMode();
  //start frame
  for(long i;i<1048576;i++){//1048576 = 1Mb
    data=readByte(address++);
    Serial.write(data);
    //checksum^=data;
  }
}
