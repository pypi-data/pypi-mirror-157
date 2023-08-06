#pragma once

namespace tx97
{
   enum Layer {
      TX_DZ = 0,
      TX_CL = 1,
      TX_DL = 2,
      TX_IB = 3,
      TX_LH = 4,
      TX_BO = 5,
      TX_RA = 6,
      TX_DP = 7,
      TX_DD = 8,
      TX_DG = 9,
      TX_LN = 10,
      TX_RT = 11,
      TX_CR = 12,
      TX_FL = 13,
      TX_TX = 14,
      TX_IN = 15,
      TX_OT = 16,
      TX_SB = 17,
      TX_HL = 18,
      TX_HG = 19,
      TX_HO = 20,
      LayersCount
   };

#pragma pack(1)

   // Кодирование текстовых строк длины не более 255 символов (1 байт)
   struct TRS_STRING
   {
      unsigned char  N;       // Длина строки
      char           Data[1]; // Собственно строка
   }; // struct TRS_STRING

   // Кодирование текстовых строк длины более 255 символов (2 байта)
   struct TRS_LONGSTRING
   {
      unsigned short N;       // Длина строки
      char           Data[1]; // Собственно строка
   };

   // Структура географических координат в формате TX97
   struct TRS_GEO_POINT
   {
      short lat;  // Широта
      short lon;  // Долгота
   }; // struct TRS_GEO_POINT

   //////////////////////////////////////////////////////////////////////////
   // Структура заголовка карты формата TX97
   struct DESCRIPTION
   {
      char  Head[15];      // Заголовок "TRANSAS CE v6.0"
      char  Date_corr[11]; // Дата последней коррекции
      char  Chart_name[9]; // Имя бумажной карты
      char  File_name[9];  // Имя электронной карты
      float Delta_lat;     // Поправка по широте для перехода к WGS
      float Delta_lon;     // Поправка по долготе для перехода к WGS
      float Latb;          // Координаты углов карты - наименьшая широтa
      float Late;          // Координаты углов карты - наибольшая широтa
      float Lonb;          // Координаты углов карты - наименьшая долгота
      float Lone;          // Координаты углов карты - наибольшая долгота
      float Latm;          // Базовая широта
      float C0;            // Масштаб исходной карты
      short year_PD;       // Год издания бумажной карты
      short month_PD;      // Месяц издания бумажной карты
      short year_PP;       // Год печати бумажной карты
      short month_PP;      // Месяц печати бумажной карты
      short year_EC;       // Год изготовления электронной карты
      short month_EC;      // Месяц изготовления электронной карты
      char  Wgs;           // Флаг для обработки WGS координат
      char  DP_mean;       // Единицы измерения глубины
      char  LH_book;       // Источник информации по секторам маяков
      char  Datum;         // Эллипсоид
      char  Proj;          // Проекция
      char  Type;          // Тип карты
      char  Cntr;          // Страна изготовитель бумажной карты
      char  LangP;         // Язык бумажной карты
      char  LangE;         // Язык электронной карты
      char  Reg;           // Регион МАМС/IALA
      char  CntG;          // Страна/гидрография владелец информации
      char  compress;      // Зарезервировано для обработки компрессии карты
      char  WaterLevel;    // Уровень воды
      char  HO_mean;       // Единицы измерения высоты
      char  TypeEx;        // Подтип карты (см. поле Type)
      char  PubNum;        // Номер издания карты
      char  CorrIssue;     // Номер выпуска последней внесенной корректуры
      char  Reserved[2];   // Зарезервировано (не используется)
      char  Revision;      // Редакция карты (должно быть равно 0)
   }; // struct DESCRIPTION

   struct DESCRIPTION_EX : DESCRIPTION
   {
      long Offsets[22]; // Таблица указателей на слои карты
   }; // struct DESCRIPTION_EX

   //////////////////////////////////////////////////////////////////////////
   // Структура наименования
   struct TAIL
   {
      TRS_LONGSTRING name; // Наименование карты
   }; // struct TAIL

   //////////////////////////////////////////////////////////////////////////
   // \brief Структура данных врезки
   struct CHARTLET
   {
      short          N;          // Количество точек в представлении полилинии
      TRS_GEO_POINT  points[1];  // Указатель на массив из N координат точек полилинии
   }; // struct CHARTLET

   //////////////////////////////////////////////////////////////////////////
   // Структура данных береговой линии
   struct COAST_LINE
   {
      short          N;          // Количество точек в представлении полилинии
      short          fs;         // Атрибуты линии
      TRS_GEO_POINT  points[1];  // Указатель на массив из N координат точек полилинии
   }; // struct COAST_LINE

   //////////////////////////////////////////////////////////////////////////
   // Структура осушек
   struct COVERS_AREA
   {
      short          N;          // Географическая координата окружности
      short          fs;         // Атрибуты линии
      TRS_GEO_POINT  points[1];  // Указатель на массив из N координат точек полилинии
   }; // struct COVERS_AREA

   //////////////////////////////////////////////////////////////////////////
   // \brief Структура изобаты
   struct ISOBATHS
   {
      short          N;          // Количество точек в представлении полилинии
      unsigned short depth;      // Значение глубины в 1/10 метра (в дециметрах)
      short          fs;         // Атрибуты линии
      TRS_GEO_POINT  points[1];  // Указатель на массив из N координат точек полилинии
   }; // struct ISOBATHS
   
   //////////////////////////////////////////////////////////////////////////
   ///Структура маяка
   struct LIGHTHOUSE
   {
      TRS_GEO_POINT  point; // Географическая координата маяка
      short          pe; // Период огня
      char           ft; // Характеристика огня
      char           nf; // Число проблесков/затмений
      char           ra; ///<Местоположение, наличие pакона и створа
      char           ns; // Количество секторов
      signed char    hl; // Высота от основания
      signed char    hs; // Высота от уровня моря
      char           rn [  8 ]; // Национальное обозначение
      char           un [ 10 ]; // Международное обозначение
      signed char    fl; // Кодирование дублирующих огней
      char           pr; // Тип маяка
      char           tf; // Тип топовой фигуры маяка
      //Далее идут бинарные блоки и TRS-строки (кодированная длительность,
      //кодированные параметры сектора, имя и пояснение)
   }; // struct LIGHTHOUSE

   // Структура закодированных параметров секторов у сложных маяков
   struct LIGHTHOUSE_INFO
   {
      char  col;  // Цвет
      char  vl;   // Видимость
      short ang;  // Начальный угол (десятые градуса)
   }; // struct LIGHTHOUSE_INFO

   /// Структура, описывающая длительность проблесков и затмений.
   struct FLASH_ECLIPSE
   {      
      char flash; ///< Проблеск.
      char eclipse; ///< Затмение.
   }; // struct FLASH_ECLIPSE

   struct LIGHTHOUSE_DESC
   {
      const LIGHTHOUSE*       pLighthouse;
      const char*             pNfInfo;
      short                   nfInfoSize;
      const LIGHTHOUSE_INFO*  pLhInfo;
      short                   lhInfoNum;
      const TRS_STRING*       pName;
      const TRS_STRING*       pNote;
   };
   
   //////////////////////////////////////////////////////////////////////////
   // Структура буя
   struct BUOY
   {
      TRS_GEO_POINT  point;   // Географическая координата буя
      short          pe;      // Период огня
      char           ft;      // Характеристика огня
      char           nf;      // Число проблесков/затмений
      char           ra;      // Признак наличия ракона
      char           tp;      // Тип буя
      char           bc;      // Цвет основания
      char           lc;      // Цвет огня
      char           rn[8];   // Национальное обозначение
      char           un[10];  // Международное обозначение
      // Далее идут TRS-строки (имя и пояснение)
   }; // struct BUOY

   struct BUOY_DESC
   {
      const BUOY*       pBuoy;
      const TRS_STRING* pName;
      const TRS_STRING* pNote;
   };

   //////////////////////////////////////////////////////////////////////////
   struct RACON
   {
      TRS_GEO_POINT  point;      // Географическая координата ракона
      char           nm;         // Признак типа ракона
      char           morse[1];   // Значение кода Морзе с которым аппаратура РЛ станции выходит в эфир
   }; // struct RACON

   //////////////////////////////////////////////////////////////////////////
   // Структура глубин
   struct DEPTHS
   {
      TRS_GEO_POINT  point;   // Географическая координата глубины
      unsigned short depth;   // Глубина
   }; // struct DEPTHS

   //////////////////////////////////////////////////////////////////////////
   // Структура высоты на осушках
   struct COVERED_HEIGHTS
   {
      TRS_GEO_POINT  point;   //  Географическая координата высоты на осушках
      unsigned short depth;   // Высота на осушке
   }; // struct COVERED_HEIGHTS

   //////////////////////////////////////////////////////////////////////////
   // Структура изолированной опасности
   struct ISOLATED_DANGER
   {
      TRS_GEO_POINT  point;   // Географическая координата изолированной опасности
      unsigned short depth;   // Значение высоты в 1/10 долях метра (дециметрах)
      char           type;    // Тип опасности
      char           exist;   // Признак существования
   }; // struct ISOLATED_DANGER

   //////////////////////////////////////////////////////////////////////////
   // Структура линейного объекта
   struct LINE
   {
      short          N;          // Количество точек в представлении полилинии
      short          color;      // Цвет линии
      short          style;      // Стиль линии
      short          fill;       // Признак замыкания линии
      short          type;       // Тип линии
      TRS_GEO_POINT  points[1];  // Указатель на массив из N координат точек полилинии
   }; // struct LINE

   //////////////////////////////////////////////////////////////////////////
   // Структура рекомендованного маршрута
   struct RECOMMENDED_ROUTE
   {
      short          N;          // Количество точек в представлении полилинии
      unsigned short depth;      // Значение глубины
      unsigned short dir1;       // Направление
      unsigned short type;       // Битовая маска
      TRS_GEO_POINT  points[1];  // Указатель на массив из N координат точек полилинии
   }; // struct RECOMMENDED_ROUTE

   //////////////////////////////////////////////////////////////////////////
   // Структура окружности
   struct CIRCLE
   {
      TRS_GEO_POINT  point;   // Географическая координата окружности
      float          r;       // Радиус в морских милях
      short          sa;      // Не используется
      short          ea;      // Не используется
      short          kind;    // Не используется
      short          color;   // Цвет линии
      short          style;   // Стиль линии
      short          fill;    // Признак замыкания линии
      short          type;    // Тип линии
   }; // struct CIRCLE

   //////////////////////////////////////////////////////////////////////////
   // Структура течения
   struct STREAM
   {
      TRS_GEO_POINT  point;         // Географическая координата течения
      short          direction[13]; // Направление ( в градусах )
      struct
      {
         char syzygy, quadrature;
      }              speed[13];     // Скорость ( сизигия и квадратура )
      short          num;           // Номер опорного пункта
   }; // struct STREAM

   //////////////////////////////////////////////////////////////////////////
   // Структура надписи
   struct TEXT
   {
      TRS_GEO_POINT  point;   // Географические координаты надписи
      short          color;   // Цвет надписи
      TRS_STRING     s;       // Текстовая строка
   }; // struct TEXT

   //////////////////////////////////////////////////////////////////////////
   // Структура информации
   struct INFORMATION
   {
      TRS_GEO_POINT  point;   // Географические координаты информации
      short          type;    // Тип информации
      // Количество строк (не соответствует спецификации: по документации должен быть 2 байта, в картах - 1 байт)
      unsigned char  num;
      TRS_STRING     s[1];    // Массив текстовых строк
   }; // struct INFORMATION

   //////////////////////////////////////////////////////////////////////////
   ///Структура, описывающая прочие объекты
   struct OTHER_OBJECT
   {
      TRS_GEO_POINT  point;   // Географические координаты прочего объекта
      short          type;    // Тип объекта
   }; // struct OTHER_OBJECT

   //////////////////////////////////////////////////////////////////////////
   // Структура грунта
   struct SEABED_NATURE
   {
      TRS_GEO_POINT  point;   // Географические координаты грунта
      TRS_STRING     s;       // Текстовая строка
   }; // struct SEABED_NATURE

   //////////////////////////////////////////////////////////////////////////
   // Структура горизонтали
   struct HORISONTAL_LANDMARKS
   {
      short          N;          // Количество точек в представлении полилинии
      unsigned short depth;      // Значение глубины / высоты
      short          type;       // Тип линии
      TRS_GEO_POINT  points[1];  // Указатель на массив из N координат точек полилинии
   }; // struct HORISONTAL_LANDMARKS

   //////////////////////////////////////////////////////////////////////////
   // Структура отличительной высоты
   struct HEIGHT
   {
      TRS_GEO_POINT  point;   // Географическая координата отличительной высоты
      unsigned short depth;   // Значение высоты в дециметрах
      short          type;    // Тип объекта
   }; // struct HEIGHT

   //////////////////////////////////////////////////////////////////////////
   // Структура берегового объекта
   struct COASTAL_FEATURE
   {
      short          N;          // Количество точек в представлении полилинии
      short          color;      // Цвет линии
      short          style;      // Стиль линии
      short          fill;       // Признак замыкания линии
      short          type;       // Тип линии
      TRS_GEO_POINT  points[1];  // Массив из N координат точек полилинии
   }; // struct COASTAL_FEATURE

#pragma pack()

   //////////////////////////////////////////////////////////////////////////

   // посимвольная сумма всех байтов, не учитывая возможное переполнение
   inline long calc_check_sum ( const void* pData, unsigned szData )
   {
      const unsigned char* pBytes = reinterpret_cast<const unsigned char*>( pData );

      long crc = 0;
      for ( unsigned i = 0; i < szData; ++i )
         crc += pBytes[ i ];

      return crc;
   }

}