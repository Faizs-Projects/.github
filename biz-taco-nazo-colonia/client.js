/**
 * Every public fact the site is allowed to say.
 * Components render this file. They do not invent hours, ratings, or dishes.
 *
 * Chain: independent Colonia counter. Not a taconazo.com location.
 * Ordering they already use: DoorDash (primary), Seamless (secondary). No first-party checkout.
 */

export const client = {
  name: "Taco Nazo",
  place: "Colonia",
  regionName: "New Jersey",
  seoTitle: "Taco Nazo Colonia | Birria, tacos, and breakfast on St. Georges Ave",
  seoDescription:
    "Independent taqueria at 1331 St Georges Ave, Colonia, NJ. Birria with consommé, street tacos, shrimp, and breakfast from 9. Order on DoorDash or call (732) 943-2006.",
  hero: {
    kicker: "Colonia · St. Georges Ave",
    loudTop: "Birria,",
    whisper: "with the",
    loudBottom: "consommé.",
    lede: "Breakfast from 9. A board big enough for a family order or a lunch break, and pozole on Sunday.",
  },
  phone: {
    display: "(732) 943-2006",
    tel: "+17329432006",
  },
  address: {
    street: "1331 St Georges Ave",
    city: "Colonia",
    region: "NJ",
    postal: "07067",
    country: "US",
  },
  geo: { lat: 40.58444, lng: -74.29317 },
  mapsUrl:
    "https://www.google.com/maps/search/?api=1&query=Taco+Nazo+1331+St+Georges+Ave+Colonia+NJ+07067",
  hours: [
    {
      days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
      label: "Monday–Saturday",
      opens: "09:00",
      closes: "23:00",
      display: "9am–11pm",
    },
    {
      days: ["Sunday"],
      label: "Sunday",
      opens: "09:00",
      closes: "22:00",
      display: "9am–10pm",
    },
  ],
  hoursNote: "Delivery apps often stop taking orders earlier than the door.",
  specialsNote: "Call for daily specials.",
  trust: [
    { label: "4.4 on Google", hrefKey: "maps" },
    { label: "4.8 · 200+ on DoorDash", hrefKey: "doordash" },
  ],
  order: {
    primary: {
      name: "DoorDash",
      label: "Order on DoorDash",
      detail: "Pickup and delivery",
      href: "https://www.doordash.com/store/taco-nazo-colonia-34703505",
    },
    secondary: {
      name: "Seamless",
      label: "Or Seamless",
      href: "https://www.seamless.com/menu/taco-nazo-1331-saint-georges-avenue-woodbridge-township/14869024",
    },
  },
  social: [
    { name: "Instagram", href: "https://www.instagram.com/taconazonj/" },
    { name: "Yelp", href: "https://www.yelp.com/biz/taco-nazo-colonia" },
  ],
  amenities: [
    "Counter seats",
    "Takeout",
    "Delivery",
    "Parking on site",
    "Pets welcome",
  ],
  platesKicker: "Start here",
  platesTitle: "Four plates people come back for",
  plates: [
    {
      name: "Tacos de birria",
      detail: "Slow-cooked beef, three to an order, consommé on the side.",
    },
    {
      name: "Elote",
      detail: "Corn on the cob. The side people mention by name.",
    },
    {
      name: "Camarones rancheros",
      detail: "Shrimp with peppers, tomato, and onion.",
    },
    {
      name: "Weekend caldos",
      detail: "Pozole and shrimp soup. Saturday and Sunday only.",
    },
  ],
  menuKicker: "The board",
  menuTitle: "Everything else the kitchen does",
  menuNote:
    "Prices live on DoorDash. They move, and that menu is the one the kitchen rings up.",
  menu: [
    {
      name: "Birria",
      note: "Slow-cooked beef",
      items: [
        { name: "Tacos de birria", detail: "Three, with consommé" },
        { name: "Quesabirria", detail: "Birria in a quesadilla" },
        { name: "Burrobirria", detail: "Birria in a burrito" },
        { name: "Torta de birria", detail: "Birria sandwich" },
        { name: "Birria box", detail: "20 tacos with consommé", lang: "en" },
        { name: "Birria de pollo", detail: "Chicken birria" },
      ],
    },
    {
      name: "Street tacos",
      note: "Onion and cilantro",
      items: [
        { name: "Pollo", detail: "Chicken" },
        { name: "Bistec", detail: "Steak" },
        { name: "Carnitas", detail: "Pork" },
        { name: "Pastor", detail: "Marinated pork" },
        { name: "Chorizo", detail: "Mexican sausage" },
        { name: "Pescado", detail: "Fish" },
        { name: "Camarones", detail: "Shrimp" },
        { name: "Lengua", detail: "Beef tongue" },
      ],
    },
    {
      name: "Tortas",
      note: "Sandwiches, served with fries",
      items: [
        { name: "Torta", detail: "Chicken, steak, pastor, or pork" },
        { name: "Torta de milanesa", detail: "Breaded chicken or steak" },
        { name: "Torta magnum", detail: "Steak or chicken, guacamole, and cheese" },
      ],
    },
    {
      name: "Burritos",
      note: "",
      items: [
        { name: "Burrito", detail: "Rice, beans, and cheese, choice of meat" },
        { name: "Burrito súper", detail: "Guacamole and fries" },
        { name: "Burrito ahogado", detail: "Green salsa and two eggs" },
        { name: "Chimichanga", detail: "Fried burrito" },
        { name: "Burrito de pescado", detail: "Tilapia" },
        { name: "Burrito de camarón", detail: "Shrimp" },
      ],
    },
    {
      name: "Quesadillas",
      note: "Flour or corn tortilla",
      items: [
        { name: "Quesadilla", detail: "Chicken, pork, pastor, steak, or sausage" },
        { name: "Quesadilla de camarón", detail: "Shrimp" },
        { name: "Quesadilla gobernador", detail: "Shrimp with peppers, onion, and tomato" },
        { name: "Quesadilla de lengua", detail: "Beef tongue" },
      ],
    },
    {
      name: "Enchiladas",
      note: "With rice and beans",
      items: [
        { name: "Enchiladas rojas", detail: "Red sauce, chicken or steak" },
        { name: "Enchiladas verdes", detail: "Green sauce, chicken or steak" },
        { name: "Enchiladas de mole", detail: "Chicken in mole" },
      ],
    },
    {
      name: "Antojitos",
      note: "",
      items: [
        { name: "Elote", detail: "Corn on the cob" },
        { name: "Guacamole", detail: "Fresh" },
        { name: "Tamales", detail: "Red or green, chicken" },
        { name: "Nacho fries", detail: "Fries with chicken or steak", lang: "en" },
        { name: "Pico de gallo", detail: "With chips" },
        { name: "Maduros", detail: "Sweet plantains" },
        { name: "Tostones", detail: "Fried plantains" },
        { name: "Flautas", detail: "Chicken, cheese, or steak" },
        { name: "Alitas", detail: "Chicken wings with fries or tostones" },
        { name: "Salchipapas", detail: "Fries and sliced hot dogs" },
      ],
    },
    {
      name: "Picaditas, sopes y huaraches",
      note: "Thick corn tortillas with beans",
      items: [
        { name: "Picaditas", detail: "Order of three" },
        { name: "Sopes", detail: "Single, or an order of three" },
        { name: "Huaraches", detail: "Single, or an order of three" },
      ],
    },
    {
      name: "Fajitas",
      note: "With rice and beans",
      items: [
        { name: "Fajitas", detail: "Steak or chicken, with peppers and onion" },
        { name: "Fajitas mixtas", detail: "Steak and chicken" },
        { name: "Fajitas de camarones", detail: "Shrimp" },
        { name: "Fajitas texanas", detail: "Steak, chicken, and shrimp" },
      ],
    },
    {
      name: "Platillos",
      note: "With rice and beans",
      items: [
        { name: "Carne asada", detail: "Grilled steak with onions" },
        { name: "Bistec a la mexicana", detail: "Steak in a tomato sauce" },
        { name: "Pechuga a la plancha", detail: "Grilled chicken" },
        { name: "Pechuga a la mexicana", detail: "Chicken in a tomato sauce" },
        { name: "Pechuga con camarones", detail: "Chicken and shrimp" },
        { name: "Milanesa", detail: "Breaded steak or chicken" },
        { name: "Alambre", detail: "Mixed grill with cheese, peppers, and onion" },
        { name: "El zarape", detail: "Steak and chicken plate" },
        { name: "Molcajete", detail: "Steak, chicken, and sausage in a molcajete" },
      ],
    },
    {
      name: "Mariscos",
      note: "",
      items: [
        { name: "Camarones a la plancha", detail: "Grilled shrimp" },
        { name: "Camarones rancheros", detail: "Shrimp with peppers, tomato, and onion" },
        { name: "Camarones a la mexicana", detail: "Mexican-style shrimp" },
        { name: "Camarones a la diabla", detail: "Shrimp in a spicy red sauce" },
        { name: "Mojarra frita", detail: "Fried tilapia" },
        { name: "Coctel de camarones", detail: "Shrimp cocktail" },
      ],
    },
    {
      name: "Breakfast",
      note: "From 9",
      items: [
        { name: "Breakfast burrito", detail: "Egg, Mexican sausage, and cheese", lang: "en" },
        { name: "Chilaquiles", detail: "Red or green, chicken or steak" },
        { name: "Huevos a la mexicana", detail: "Eggs with tomato, onion, and pepper" },
        { name: "Huevos con chorizo", detail: "Eggs and Mexican sausage" },
        { name: "Huevos con jamón", detail: "Eggs and ham" },
      ],
    },
    {
      name: "Weekend caldos",
      note: "Saturday and Sunday only",
      items: [
        { name: "Pozole", detail: "Hominy soup" },
        { name: "Caldo de camarones", detail: "Shrimp soup" },
      ],
    },
    {
      name: "Bowls",
      note: "",
      items: [
        { name: "Taco salad bowl", detail: "Rice, beans, cheese, salad, and avocado", lang: "en" },
        { name: "Shrimp bowl", detail: "Rice, beans, and cheese", lang: "en" },
        { name: "Mix salad", detail: "Chicken, steak, and shrimp", lang: "en" },
        { name: "Vegetarian burrito", detail: "Rice, beans, and cheese", lang: "en" },
        { name: "Vegetarian super burrito", detail: "Vegetables and cheese", lang: "en" },
      ],
    },
    {
      name: "Drinks and dessert",
      note: "",
      items: [
        { name: "Aguas frescas", detail: "Horchata, jamaica, or tamarindo" },
        { name: "Jarritos", detail: "Lime, piña, mandarina, tamarindo, or fruit punch" },
        { name: "Tres leches", detail: "The cake people save room for" },
      ],
    },
  ],
  visitKicker: "The counter",
  visitTitle: "Come in, or call it in.",
  orderRow: "Ready when you are.",
  affiliation:
    "Taco Nazo at 1331 St Georges Ave is an independent restaurant in Colonia, New Jersey. It is not part of the Taco Nazo restaurants in Southern California, and this page is not affiliated with Taco Nazo Corp.",
  demoNote:
    "Demo website prepared from public listings. Confirm hours and the board with the counter before you treat this as the printed menu.",
};
