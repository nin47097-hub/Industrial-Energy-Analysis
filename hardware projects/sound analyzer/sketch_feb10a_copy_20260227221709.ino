#include <LiquidCrystal.h>


LiquidCrystal lcd(7, 8, 9, 10, 11, 12);


const int micPin = A0;


float smoothed = 0;      
float baseline = 0;      
int level = 0;


const int threshold = 2;       
const int maxDiff = 100;        
const float smoothingFactor = 0.7;  
const float baselineFactor = 0.995;

void setup() {
  lcd.begin(16, 2);            
  lcd.print("Sound Level:"); 
  Serial.begin(9600);           

  
  baseline = analogRead(micPin);
  smoothed = baseline;
  Serial.print("Initial Baseline: ");
  Serial.println(baseline);
}

void loop() {

  int micRaw = analogRead(micPin);
  smoothed = smoothingFactor * smoothed + (1 - smoothingFactor) * micRaw;


  baseline = baselineFactor * baseline + (1 - baselineFactor) * smoothed;

 
  int diff = abs(smoothed - baseline);


  if(diff < threshold) diff = 0;

  level = map(diff, 0, maxDiff, 0, 16);
  level = constrain(level, 0, 16);

  lcd.setCursor(12, 0);
  if(diff < 10) lcd.print("   ");      
  else if(diff < 100) lcd.print("  ");
  else lcd.print(" ");
  lcd.print(diff);


  lcd.setCursor(0, 1);
  for(int i = 0; i < 16; i++){
    if(i < level) lcd.write(byte(255)); 
    else lcd.print(" ");                 
  }

  
  Serial.print("Mic: "); Serial.print(micRaw);
  Serial.print(" Smoothed: "); Serial.print(smoothed);
  Serial.print(" Baseline: "); Serial.print(baseline);
  Serial.print(" Diff: "); Serial.println(diff);

  delay(50); 
}