/* ==========================================
   MILK LAND POS - Main JavaScript
   ========================================== */

// ---- Sidebar toggle (mobile) ----
document.addEventListener('DOMContentLoaded', function () {
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebarOverlay');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function () {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('d-none');
    });
  }

  if (overlay) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('open');
      overlay.classList.add('d-none');
    });
  }

  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // Confirm delete
  document.querySelectorAll('[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      const msg = this.dataset.confirm || 'Are you sure?';
      if (!confirm(msg)) e.preventDefault();
    });
  });
});

/* ==========================================
   POS SYSTEM
   ========================================== */

const POS = (function () {
  let cart = [];
  let userEditedPaid = false;

  function formatCurrency(amount) {
    return 'PKR ' + parseFloat(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function getCartIndex(productId) {
    return cart.findIndex(function (i) { return i.product_id == productId; });
  }

  function addProduct(productId, name, price, stock, unit) {
    if (stock <= 0) {
      showToast('Out of stock: ' + name, 'danger');
      return;
    }
    userEditedPaid = false;
    const idx = getCartIndex(productId);
    if (idx >= 0) {
      if (cart[idx].qty >= stock) {
        showToast('Max stock reached for ' + name, 'warning');
        return;
      }
      cart[idx].qty++;
    } else {
      cart.push({
        product_id: productId,
        name: name,
        rate: parseFloat(price),
        qty: 1,
        stock: parseFloat(stock),
        unit: unit
      });
    }
    renderCart();
  }

  function removeItem(idx) {
    userEditedPaid = false;
    cart.splice(idx, 1);
    renderCart();
  }

  function changeQty(idx, delta) {
    userEditedPaid = false;
    cart[idx].qty += delta;
    if (cart[idx].qty <= 0) {
      cart.splice(idx, 1);
    } else if (cart[idx].qty > cart[idx].stock) {
      cart[idx].qty = cart[idx].stock;
      showToast('Maximum stock reached', 'warning');
    }
    renderCart();
  }

  function renderCart() {
    const cartEl = document.getElementById('cartItems');
    const emptyEl = document.getElementById('cartEmpty');
    if (!cartEl) return;

    if (cart.length === 0) {
      cartEl.innerHTML = '';
      if (emptyEl) emptyEl.style.display = 'block';
    } else {
      if (emptyEl) emptyEl.style.display = 'none';
      cartEl.innerHTML = cart.map(function (item, idx) {
        const lineTotal = item.qty * item.rate;
        return '<div class="cart-item">' +
          '<div class="cart-item-top">' +
          '<span class="cart-item-name">' + item.name + '</span>' +
          '<button class="cart-item-remove" onclick="POS.removeItem(' + idx + ')" title="Remove">&times;</button>' +
          '</div>' +
          '<div class="cart-item-bottom">' +
          '<div class="qty-control">' +
          '<button class="qty-btn" onclick="POS.changeQty(' + idx + ', -1)">−</button>' +
          '<span class="qty-display">' + item.qty + '</span>' +
          '<button class="qty-btn" onclick="POS.changeQty(' + idx + ', 1)">+</button>' +
          '</div>' +
          '<span class="cart-item-total">' + formatCurrency(lineTotal) + '</span>' +
          '</div>' +
          '<div style="font-size:0.7rem;color:#9CA3AF">@ ' + formatCurrency(item.rate) + ' / ' + item.unit + '</div>' +
          '</div>';
      }).join('');
    }

    updateTotals();
    syncHiddenInput();
  }

  function updateTotals() {
    const subtotal = cart.reduce(function (sum, i) { return sum + i.qty * i.rate; }, 0);
    const discPctEl = document.getElementById('discountPct');
    const discPct = discPctEl ? parseFloat(discPctEl.value) || 0 : 0;
    const discAmount = subtotal * discPct / 100;
    const grandTotal = subtotal - discAmount;
    const paidEl = document.getElementById('paidAmount');
    if (paidEl && !userEditedPaid) {
      paidEl.value = grandTotal.toFixed(2);
    }
    const paid = paidEl ? parseFloat(paidEl.value) || 0 : 0;
    const balance = Math.max(grandTotal - paid, 0);
    const change = paid > grandTotal ? paid - grandTotal : 0;

    setText('subtotalDisplay', formatCurrency(subtotal));
    setText('discAmountDisplay', formatCurrency(discAmount));
    setText('grandTotalDisplay', formatCurrency(grandTotal));
    setText('paidDisplay', formatCurrency(paid));
    setText('balanceDisplay', formatCurrency(balance));

    const changeRow = document.getElementById('changeRow');
    const balanceRow = document.getElementById('balanceRow');
    if (changeRow && balanceRow) {
      if (change > 0) {
        changeRow.style.display = 'flex';
        setText('changeDisplay', formatCurrency(change));
        balanceRow.style.display = 'none';
      } else {
        changeRow.style.display = 'none';
        balanceRow.style.display = 'flex';
      }
    }
  }

  function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function syncHiddenInput() {
    const input = document.getElementById('itemsData');
    if (input) input.value = JSON.stringify(cart);
  }

  function filterProducts(query) {
    const q = query.toLowerCase();
    document.querySelectorAll('.product-card').forEach(function (card) {
      const name = (card.dataset.name || '').toLowerCase();
      const cat = (card.dataset.category || '').toLowerCase();
      card.style.display = (name.includes(q) || cat.includes(q) || q === '') ? '' : 'none';
    });
  }

  function filterByCategory(cat) {
    document.querySelectorAll('.product-card').forEach(function (card) {
      if (!cat || card.dataset.category === cat) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
    document.querySelectorAll('.pill-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.dataset.cat === cat);
    });
  }

  function submitSale() {
    if (cart.length === 0) {
      showToast('Cart is empty. Add products first.', 'danger');
      return false;
    }
    const saleType = document.getElementById('saleType') ? document.getElementById('saleType').value : 'Cash';
    const customerId = document.getElementById('customerId') ? document.getElementById('customerId').value : '';
    if (saleType === 'Credit' && !customerId) {
      showToast('Please select a customer for credit sale.', 'danger');
      return false;
    }
    syncHiddenInput();
    return true;
  }

  function showToast(msg, type) {
    type = type || 'info';
    const toast = document.createElement('div');
    toast.className = 'alert alert-' + type + ' position-fixed';
    toast.style.cssText = 'bottom:20px;right:20px;z-index:9999;min-width:250px;font-size:0.85rem;';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(function () { toast.remove(); }, 3000);
  }

  return {
    addProduct: addProduct,
    removeItem: removeItem,
    changeQty: changeQty,
    filterProducts: filterProducts,
    filterByCategory: filterByCategory,
    submitSale: submitSale,
    updateTotals: updateTotals,
    showToast: showToast,
    getCart: function () { return cart; },
    markPaidEdited: function () { userEditedPaid = true; },
    resetPaidEdited: function () { userEditedPaid = false; updateTotals(); }
  };
})();

// POS Search handler
document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('productSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      POS.filterProducts(this.value);
    });
  }

  const discInput = document.getElementById('discountPct');
  if (discInput) {
    discInput.addEventListener('input', POS.updateTotals);
  }

  const paidInput = document.getElementById('paidAmount');
  if (paidInput) {
    paidInput.addEventListener('input', function () {
      POS.markPaidEdited();
      POS.updateTotals();
    });
  }

  const saleForm = document.getElementById('saleForm');
  if (saleForm) {
    saleForm.addEventListener('submit', function (e) {
      if (!POS.submitSale()) e.preventDefault();
    });
  }

  // Category pill "All"
  const allPill = document.getElementById('pillAll');
  if (allPill) {
    allPill.classList.add('active');
    allPill.addEventListener('click', function () {
      POS.filterByCategory('');
    });
  }
});

// Purchase form: dynamic item rows
const PurchaseForm = (function () {
  let items = [];
  let productData = {};

  function init(products) {
    productData = {};
    products.forEach(function (p) {
      productData[p.id] = p;
    });
    addRow();
  }

  function addRow() {
    items.push({ product_id: '', qty: 1, rate: 0 });
    renderRows();
  }

  function removeRow(idx) {
    items.splice(idx, 1);
    if (items.length === 0) addRow();
    else renderRows();
  }

  function updateItem(idx, field, value) {
    items[idx][field] = value;
    if (field === 'product_id' && productData[value]) {
      items[idx].rate = parseFloat(productData[value].purchase_price);
    }
    renderRows();
  }

  function renderRows() {
    const tbody = document.getElementById('purchaseItemsBody');
    if (!tbody) return;

    let total = 0;
    const productOptions = Object.values(productData).map(function (p) {
      return '<option value="' + p.id + '">' + p.name + ' (' + p.unit_type + ')</option>';
    }).join('');

    tbody.innerHTML = items.map(function (item, idx) {
      const lineTotal = parseFloat(item.qty || 0) * parseFloat(item.rate || 0);
      total += lineTotal;
      return '<tr>' +
        '<td><select class="form-select form-select-sm" onchange="PurchaseForm.updateItem(' + idx + ',\'product_id\',this.value)">' +
        '<option value="">-- Select --</option>' + productOptions + '</select></td>' +
        '<td><input type="number" class="form-control form-control-sm" value="' + item.qty + '" min="0.01" step="0.01" onchange="PurchaseForm.updateItem(' + idx + ',\'qty\',this.value)"></td>' +
        '<td><input type="number" class="form-control form-control-sm" value="' + item.rate + '" min="0" step="0.01" onchange="PurchaseForm.updateItem(' + idx + ',\'rate\',this.value)"></td>' +
        '<td><strong>PKR ' + lineTotal.toFixed(2) + '</strong></td>' +
        '<td><button type="button" class="btn btn-sm btn-outline-danger" onclick="PurchaseForm.removeRow(' + idx + ')">&times;</button></td>' +
        '</tr>';
    }).join('');

    const totalEl = document.getElementById('purchaseTotal');
    if (totalEl) totalEl.textContent = 'PKR ' + total.toFixed(2);

    syncHidden();
  }

  function syncHidden() {
    const input = document.getElementById('purchaseItemsData');
    if (input) input.value = JSON.stringify(items);
  }

  function submit() {
    const valid = items.some(function (i) { return i.product_id && parseFloat(i.qty) > 0; });
    if (!valid) {
      alert('Please add at least one product with valid quantity.');
      return false;
    }
    syncHidden();
    return true;
  }

  return { init: init, addRow: addRow, removeRow: removeRow, updateItem: updateItem, submit: submit };
})();
