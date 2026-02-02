using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace _15._10._2025_KULLANICI_GIRISI
{
    public partial class Form2 : Form
    {
        public Form2(string kadi)
        {
            InitializeComponent();
            label1.Text = "Aktif Kullanıcı : " + kadi;
        }

        private void Form2_Load(object sender, EventArgs e)
        {
            
        }
    }
}
