#pragma once

namespace tx97 {

// Типы проекций
namespace projection {
   int const Mercator            = 0; // Mercator
   int const TransverseMercator  = 1; // Transverse Mercator
   int const Gnomonic            = 2; // Gnomonic
   int const Polyconic           = 3; // Polyconic
   int const Gauss               = 4; // Gauss
   int const UTM                 = 5; // UTM
}


// Коды элипсоида
namespace ellipsoid {
   int const Krassovsky          = 0;  // Krassovsky
   int const Airy                = 1;  // Airy
   int const ModAiry             = 2;  // Mod. Airy
   int const AustralNation       = 3;  // Austral. Nation.
   int const Bessel_1841         = 4;  // Bessel 1841
   int const BesselNamibia_1841  = 5;  // Bessel 1841(Namibia)
   int const Clarke_1866         = 6;  // Clarke 1866
   int const Clarke_1880         = 7;  // Clarke 1880
   int const EverestBrunei       = 8;  // Everest(Brunei)
   int const EverestIndia_1830   = 9;  // Everest(India 1830)
   int const EverestIndia_1956   = 10; // Everest(India 1956)
   int const EverestMalasia_1948 = 11; // Everest(W Malasia 1948)
   int const EverestMalasia_1969 = 12; // Everest(W Malasia 1969)
   int const ModEverest          = 13; // Mod.Everest
   int const Fischer_1960        = 14; // Fischer 1960 /Mercury/
   int const ModFischer_1960     = 15; // Mod. Fischer 1960
   int const Fischer_1968        = 16; // Fischer 1968
   int const GRS_1967            = 17; // GRS 1967
   int const GRS_1980            = 18; // GRS 1980
   int const Helmert_1906        = 19; // Helmert 1906
   int const Hough               = 20; // Hough
   int const International       = 21; // International
   int const SouthAmerican_1969  = 22; // South American 1969
   int const WGS_60              = 23; // WGS 60
   int const WGS_66              = 24; // WGS 66
   int const WGS_72              = 25; // WGS 72
   int const WGS_84              = 26; // WGS 84
   int const Unknown             = 27; // Unknown
   int const Everest             = 28; // Everest
}


// Единицы измерения глубин/высот.
namespace depth_height_unit {
   int const Metre      = 0;  // метры
   int const Foot       = 1;  // футы
   int const FootSazhen = 2;  // футы+сажени
   int const Sazhen     = 3;  // сажени
}


// Страна-изготовитель бумажной карты
namespace chart_provider {
   int const Russia_P               = 0;  // Россия
   int const England_P              = 1;  // Англия
   int const USA_P                  = 2;  // USA
   int const France_P               = 3;  // Франция
   int const Norway_P               = 4;  // Норвегия
   int const Sweden_P               = 5;  // Швеция
   int const Finland_P              = 6;  // Финляндия
   int const Germany_P              = 7;  // Германия
   int const Australia_P            = 8;  // Австралия
   int const NewZealand_P           = 9;  // Н.Зеландия
   int const IntOrganisations_P     = 10; // Международные организации
   int const Denmark_P              = 11; // Дания
   int const Holland_P              = 12; // Голландия
   int const SouthKorea_P           = 13; // Ю.Корея
   int const Spain_P                = 14; // Испания
   int const Canada_P               = 15; // Канада
   int const SouthAfricanRepublic_P = 16; // ЮАР
   int const India_P                = 17; // Индия
   int const Brazil_P               = 18; // Бразилия
   int const Surinam_P              = 19; // Суринам
   int const Poland_P               = 20; // Польша
   int const Argentina_P            = 21; // Аргентина
   int const Ecuador_P              = 22; // Эквадор
   int const Italy_P                = 23; // Италия
   int const Latvia_P               = 24; // Латвия
   int const Estonia_P              = 25; // Эстония
   int const Chile_P                = 26; // Чили
   int const Iceland_P              = 27; // Исландия
   int const Indonesia_P            = 28; // Индонезия
   int const Croatia_P              = 29; // Хорватия
}


// Страна/гидрография-владелец информации
namespace information_owner {
   int const NotDefined_I           = 0;  // Не определена
   int const Russia_I               = 1;  // Россия
   int const England_I              = 2;  // Англия
   int const USA_I                  = 3;  // USA
   int const France_I               = 4;  // Франция
   int const Norway_I               = 5;  // Норвегия
   int const Sweden_I               = 6;  // Швеция
   int const Finland_I              = 7;  // Финляндия
   int const Germany_I              = 8;  // Германия
   int const Australia_I            = 9;  // Австралия
   int const NewZealand_I           = 10; // Н.Зеландия
   int const Denmark_I              = 11; // Дания
   int const Holland_I              = 12; // Голландия
   int const SouthKorea_I           = 13; // Ю.Корея
   int const Spain_I                = 14; // Испания
   int const Canada_I               = 15; // Канада
   int const SouthAfricanRepublic_I = 16; // ЮАР
   int const India_I                = 17; // Индия
   int const Brazil_I               = 18; // Бразилия
   int const Surinam_I              = 19; // Суринам
   int const Poland_I               = 20; // Польша
   int const Argentina_I            = 21; // Аргентина
   int const Ecuador_I              = 22; // Эквадор
   int const Italy_I                = 23; // Италия
   int const Latvia_I               = 24; // Латвия
   int const Estonia_I              = 25; // Эстония
   int const Chile_I                = 26; // Чили
   int const Iceland_I              = 27; // Исландия
   int const Indonesia_I            = 28; // Индонезия
   int const Croatia_I              = 29; // Хорватия
}


// Регион МАМС/IALA
namespace region {
   int const A = 0;
   int const B = 1;
}


// Уровень воды
namespace water_level_type {
   int const Full      = 0;   // Полная
   int const Few       = 1;   // Малая
   int const UnDefined = 2;   // Не определена
}


// Источник информации по секторам  маяков
namespace information_sourse {
   int const RussianBook  = 0; // По русским книгам
   int const EnglishBook  = 1; // По английским книгам
   int const AmericanBook = 2; // По американским книгам
}


// Язык бумажной/электронной карты
namespace language {
   int const Russian    = 0;  // Русский
   int const English    = 1;  // Английский
   int const French     = 2;  // Французский
   int const Norwegian  = 3;  // Норвежский
   int const Swedish    = 4;  // Шведский
   int const Finnish    = 5;  // Финский
   int const German     = 6;  // Немецкий
   int const Dutch      = 7;  // Голландский
   int const Danish     = 8;  // Датский
   int const Portuguese = 9;  // Португальский
   int const Polish     = 10; // Польский
   int const Spanish    = 11; // Испанский
   int const Italian    = 12; // Итальянский
}

// Атрибуты линии изобаты
namespace isobaths_fs {
   int const FillRT     = 0x0001;  // Направление обхода при вводе точек против часовой стрелки
   int const RESERVED   = 0x0002;  // Не определено
   int const AR_CO      = 0x0004;  // Область равных глубин
   int const FillOut    = 0x0008;  // Меньшая глубина снаружи
   int const BreakLine  = 0x0010;  // Линия не замкнута
}

//////////////////////////////////////////////////////////////////////////
// тип огня маяка
namespace lighthouse_ft {
   int const Unknown                         = 0;  // Неизвестный
   int const Fixed                           = 1;  // Постоянный
   int const Isophase                        = 2;  // Изофазный
   int const Flashing                        = 3;  // Проблесковый
   int const GroupFlashing                   = 4;  // Гр. проблесковый
   int const CompositeGroupFlashing          = 5;  // Сл. гр. проблесковый
   int const Occulting                       = 6;  // Затмевающийся
   int const GroupOcculting                  = 7;  // Гр.затмевающийся
   int const CompositeGroupOcculting         = 8;  // Сл. гр. затмевающийся
   int const LongFlashing                    = 9;  // Дл.проблесковый
   int const GroupLongFlashing               = 10; // Гр. дл. проблесковый
   int const MorseCode                       = 11; // По азбуке Морзе
   int const Quick                           = 12; // Частый
   int const GroupQuick                      = 13; // Гр. частый
   int const GroupQuickAndLongFlashing       = 14; // Гр. частый с дл. пробл.
   int const InterruptedQuick                = 15; // Прер. частый
   int const VeryQuick                       = 16; // Очень частый
   int const GroupVeryQuick                  = 17; // Гр. очень частый
   int const GroupVeryQuickAndLongFlashing   = 18; // Гр. оч. частый с дл. пробл.
   int const InterruptedVeryQuick            = 19; // Прер. очень частый
   int const UltraQuick                      = 20; // Ультрачастый
   int const InterruptedUltraQuick           = 21; // Прер. ультрачастый
   int const FixedOcculting                  = 22; // Постоянный с затм.
   int const FixedAndGroupOcculting          = 23; // Постоянный с гр. затм.
   int const FixedIsophase                   = 24; // Постоянный с изофазным
   int const FixedFlashing                   = 25; // Постоянный с пробл.
   int const FixedAndGroupFlashing           = 26; // Постоянный с гр. пробл.
   int const FixedLongflashing               = 27; // Постоянный с дл. пробл.
   int const Alternating                     = 28; // Переменный
   int const AlternatingOcculting            = 29; // Переменный затм.
   int const AlternatingFlashing             = 30; // Переменный пробл.
   int const AlternatingGroupFlashing        = 31; // Переменный гр. пробл.
}

// типы, для которых не кодируется nf_info
const int NoNfInfoTypes[] = {
   lighthouse_ft::Unknown,  // Не совпадает с документацией (из Sahara)
   lighthouse_ft::Fixed, 
   lighthouse_ft::Isophase, 
   lighthouse_ft::Quick, 
   lighthouse_ft::VeryQuick,
   lighthouse_ft::UltraQuick
};

inline bool is_nf_info_type ( int ft )
{
   return ( std::find(NoNfInfoTypes, NoNfInfoTypes + _countof(NoNfInfoTypes), ft) == NoNfInfoTypes + _countof(NoNfInfoTypes) );
}

// флаги наличия ракона и створа маяка
namespace lighthouse_ra {
   int const RaconIsAbsent          = 0x01;
   int const RaconIsAvailable       = 0x02;
   int const RaconIsAbsentInSea     = 0x03;
   int const RaconIsAvailableInSea  = 0x04;

   int const RangeIsAvailable = 0x80;  // Наличие створа
}

// Тип топовой фигуры маяка
namespace lighthouse_tp {
   int const Undefined           = 1;  // Не определено
   int const NorthMark           = 2;  // Северный
   int const SouthMark           = 3;  // Южный
   int const EastMark            = 4;  // Восточный
   int const WestMark            = 5;  // Западный
   int const IsolatedDanger      = 6;  // Над опасностью
   int const PortHandMark        = 7;  // Левый
   int const StarboardHandMark   = 8;  // Правый
   int const SpecialMark         = 9;  // Специального назначения
   int const SafeWaterMark       = 10; // Середины фарватера
}

//////////////////////////////////////////////////////////////////////////
// цвет огня буя/бикона
namespace light_color {
   char const NoLight = 0;
   char const Red     = 1;
   char const Green   = 2;
   char const White   = 3;
   char const Blue    = 4;
   char const Yellow  = 5;
   char const Violet  = 6;
   char const Amber   = 7;
   char const Orange  = 8;
}

// Тип буя
namespace buoy_tp {
   int const Buoy                 = 1; 
   int const NorthCardinalBuoy    = 2; 
   int const SouthCardinalBuoy    = 3; 
   int const EastCardinalBuoy     = 4; 
   int const WestCardinalBuoy     = 5; 
   int const Beacon               = 6; 
   int const SparBuoy             = 7; 
   int const IsolatedDangerBuoy   = 8; 
   int const PortHandBuoy         = 9; 
   int const StarboardHandBuoy    = 10;
   int const SpecialBuoy          = 11;
   int const SafeWaterBuoy        = 12;
   int const Platform             = 13;
   int const NorthCardinalBeacon  = 14;
   int const SouthCardinalBeacon  = 15;
   int const EastCardinalBeacon   = 16;
   int const WestCardinalBeacon   = 17;
   int const IsolatedDangerBeacon = 18;
   int const PortHandBeacon       = 19;
   int const StarboardHandBeacon  = 20;
   int const SpecialPurposeBeacon = 21;
   int const MooringBuoy          = 22;
   int const FixedPoint           = 23;
   int const Pole                 = 24;
   int const Cairn                = 25;
}

}