import unittest
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'FashionHub', response.data)
        self.assertIn(b'Classic White T-Shirt', response.data)

    def test_product_detail(self):
        response = self.app.get('/product/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Classic White T-Shirt', response.data)

    def test_product_not_found(self):
        response = self.app.get('/product/999')
        self.assertEqual(response.status_code, 404)

    def test_cart(self):
        response = self.app.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your Shopping Cart', response.data)

    def test_add_to_cart(self):
        response = self.app.get('/add_to_cart/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Classic White T-Shirt', response.data)
        # Check if cart count increased in navbar (assuming it was 0)
        self.assertIn(b'Cart (1)', response.data)

    def test_checkout_get(self):
        response = self.app.get('/checkout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Checkout', response.data)

if __name__ == '__main__':
    unittest.main()
