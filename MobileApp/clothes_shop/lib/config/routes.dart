import 'package:go_router/go_router.dart';
import 'package:clothes_shop/screens/home/home_screen.dart';
import 'package:clothes_shop/screens/shop/shop_screen.dart';
import 'package:clothes_shop/screens/shop/catalog_screen.dart';
import 'package:clothes_shop/screens/cart/cart_screen.dart';
import 'package:clothes_shop/screens/checkout/checkout_screen.dart';
import 'package:clothes_shop/screens/invoice/invoice_screen.dart';
import 'package:clothes_shop/screens/wishlist/wishlist_screen.dart';
import 'package:clothes_shop/screens/about/about_screen.dart';
import 'package:clothes_shop/screens/contact/contact_screen.dart';
import 'package:clothes_shop/screens/track_order/track_order_screen.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/shop',
        builder: (context, state) => const ShopScreen(),
      ),
      GoRoute(
        path: '/catalog',
        builder: (context, state) => const CatalogScreen(),
      ),
      GoRoute(
        path: '/cart',
        builder: (context, state) => const CartScreen(),
      ),
      GoRoute(
        path: '/checkout',
        builder: (context, state) => const CheckoutScreen(),
      ),
      GoRoute(
        path: '/invoice',
        builder: (context, state) => InvoiceScreen(),
      ),
      GoRoute(
        path: '/wishlist',
        builder: (context, state) => const WishlistScreen(),
      ),
      GoRoute(
        path: '/about',
        builder: (context, state) => const AboutScreen(),
      ),
      GoRoute(
        path: '/contact',
        builder: (context, state) => const ContactScreen(),
      ),
      GoRoute(
        path: '/track-order',
        builder: (context, state) => const TrackOrderScreen(),
      ),
    ],
  );
}
