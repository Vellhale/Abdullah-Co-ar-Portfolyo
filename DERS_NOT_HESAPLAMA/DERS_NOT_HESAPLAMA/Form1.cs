using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO;

namespace DERS_NOT_HESAPLAMA
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            this.Text = "Ders Not Hesaplama " + DateTime.Now;


        }

        private void textBox3_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar >= 48 && e.KeyChar <= 57 || e.KeyChar ==8)
            {
                e.Handled = false;
            }
            else
            {
                e.Handled = true;
            }
            if (e.KeyChar == 13) { textBox4.Focus(); }


        }

        private void textBox4_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar >= 48 && e.KeyChar <= 57 || e.KeyChar == 8)
            {
                e.Handled = false;
            }
            else
            {
                e.Handled = true;
            }
            if (e.KeyChar == 13) { textBox5.Focus(); }
        }

        private void textBox5_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar >= 48 && e.KeyChar <= 57 || e.KeyChar == 8)
            {
                e.Handled = false;
            }
            else
            {
                e.Handled = true;
            }
            if (e.KeyChar == 13) { button1.Focus(); }
        }

        private void textBox1_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar >=65 && e.KeyChar <=90 ||
               e.KeyChar >=97 && e.KeyChar <=122  ||
            e.KeyChar == 8)
            {
                e.Handled = false;
            }
            else
            {
                e.Handled = true;
            }
            if (e.KeyChar == 13) { textBox2.Focus(); }
        }

        private void textBox2_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar >= 65 && e.KeyChar <= 90 ||
               e.KeyChar >= 97 && e.KeyChar <= 122 ||
            e.KeyChar == 8)
            {
                e.Handled = false;
            }
            else
            {
                e.Handled = true;
            }
            if (e.KeyChar == 13) { textBox3.Focus(); }
        }

        private void textBox3_TextChanged(object sender, EventArgs e)
        {
            int kontrol;
            if (int.TryParse(textBox3.Text , out kontrol ))
            {
                if(kontrol>100)
                {
                    MessageBox.Show("100 den büyük sayı yazamazsın!!!");
                    textBox3.Clear();
                }

            }


        }

        private void textBox4_TextChanged(object sender, EventArgs e)
        {
            int kontrol;
            if (int.TryParse(textBox4.Text, out kontrol))
            {
                if (kontrol > 100)
                {
                    MessageBox.Show("100 den büyük sayı yazamazsın!!!");
                    textBox4.Clear();
                }

            }
        }

        private void textBox5_TextChanged(object sender, EventArgs e)
        {
            int kontrol;
            if (int.TryParse(textBox5.Text, out kontrol))
            {
                if (kontrol > 100)
                {
                    MessageBox.Show("100 den büyük sayı yazamazsın!!!");
                    textBox5.Clear();
                }

            }
        }
        DialogResult mavi;
        Int32 vize, final, odev; double ortalama;
        string durumu = ""; string harf_notu = "";
        private void button1_Click(object sender, EventArgs e)
        {
            if (textBox1.Text == "" ||
                textBox2.Text =="")
            {
                MessageBox.Show("ÖĞRENCİNİN ADI - SOYADI BOŞ OLAMAZ");
                return;
            }
            if (comboBox1.SelectedIndex == -1)
            {
                MessageBox.Show("SINAV OLDUĞU DERSİ SEÇİNİZ");
                return;
            }
            if (textBox3.Text == "" ||
              textBox4.Text == "" || textBox5.Text =="")
            {
                MessageBox.Show("ÖĞRENCİNİN VİZE - FİNAL - ÖDEV NOTLARI BOŞ OLAMAZ");
                return;
            }

            //İŞLEM KAYIT
            mavi =MessageBox.Show (textBox1.Text +" "+
                textBox2.Text +" isimli öğrenci kaydı yapılsın mı?",
                "ÖĞRENCİ KAYIT",MessageBoxButtons.YesNo ,
                MessageBoxIcon.Question );
            if (mavi == DialogResult.Yes)
            {
                vize = Convert.ToInt32(textBox3.Text);
                final  = Convert.ToInt32(textBox4.Text);
                odev  = Convert.ToInt32(textBox5.Text);
                ortalama = vize * 0.30 + final * 0.60 + odev * 0.10;
                if (ortalama < 60)
                {
                    durumu = "DERSTEN KALDI";
                }
                else 
                {
                durumu ="DERSTEN GEÇTİ";
                }
                //0-34ff 35-40fd 41-50dd 51-59dc 60-70cc 7180bc 8190ba 91100aa
                if (ortalama >= 0 && ortalama <= 34) {harf_notu="FF"; }
                if (ortalama >= 35 && ortalama <= 40) { harf_notu = "FD"; }
                if (ortalama >= 41 && ortalama <= 50) { harf_notu = "DD"; }
                if (ortalama >= 51 && ortalama <= 59) { harf_notu = "DC"; }
                if (ortalama >= 60 && ortalama <= 70) { harf_notu = "CC"; }
                if (ortalama >= 71 && ortalama <= 80) { harf_notu = "CB"; }
                if (ortalama >= 81 && ortalama <= 90) { harf_notu = "BB"; }
                if (ortalama >= 91 && ortalama <= 100) { harf_notu = "AA"; }
                listBox1.Items.Add(textBox1.Text+" "+textBox2.Text+" "+comboBox1.SelectedItem+" "+ ortalama+ " "+durumu+" "+harf_notu);
                StreamWriter kaydet = new StreamWriter("kayit.txt", true, Encoding.Default);
                kaydet.WriteLine(textBox1.Text + " " + textBox2.Text + " " + comboBox1.SelectedItem + " " + ortalama + " " + durumu + " " + harf_notu);
                kaydet.Close();
                MessageBox.Show("TÜM BİLGİLER KAYDEDİLDİ");
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void comboBox1_SelectedIndexChanged(object sender, EventArgs e)
        {

        }
    }
}
