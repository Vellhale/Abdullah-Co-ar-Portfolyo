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
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {
            if (checkBox1.Checked == true)
            {
             textBox3.PasswordChar ='\0';
            }
            else 
            
            {
                textBox3.PasswordChar = '*';
            }
        }
        
        Int32 sayac = 3;
        //public static  string kadi = "ABDULLAH"; 
        string kadi = "ABDULLAH"; 
        string sifre = "2025";
        private void button1_Click(object sender, EventArgs e)
        {

            

            if (textBox1.Text.Trim() == "")
            {
                MessageBox.Show("LÜTFEN KULLANICI ADINI GİRİNİZ");
                textBox1.Focus();
                textBox1.BackColor = Color.Aqua; 
                return;
            }

            if (textBox2.Text.Trim() == "")
            {
                MessageBox.Show("LÜTFEN ŞİFRENİZİ GİRİNİZ");
                textBox2.Focus();
                textBox2.BackColor = Color.Aqua; 
                return;
            }

            if (textBox3.Text.Trim() == "")
            {
                MessageBox.Show("LÜTFEN ŞİFRE TEKRARINIZI GİRİNİZ");
                textBox3.Focus();
                textBox3.BackColor = Color.Aqua; 
                return;
            }

            if (textBox2.Text.Trim() == textBox3.Text.Trim())
            {
                if (textBox1.Text.Trim() == kadi &&
                    textBox2.Text.Trim() == sifre)
                {
                    timer1.Enabled = true;

                }

                else

                {
                    //sayac--;
                    sayac = sayac - 1;
                    //sayac -= -1;
             MessageBox.Show("KULLANICI ADI VE ŞİFRESİ YANLIŞ.\n\n               Kalan Hakkınız : "+sayac );
             if (sayac == 0)
             {
                 Application.Exit();
             }

                }

            }
            else 
            {

                MessageBox.Show("ŞİFRE ve ŞİFRE TEKRARI UYUŞMUYOR!");
                textBox2.Clear(); textBox3.Clear();
            }




        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            //progressBar1.Value = progressBar1.Value + 2;
            progressBar1.Value += 2;
            label4.Text = "Program yükleniyor %" +
                progressBar1.Value;
            if (progressBar1.Value == 100)
            {
                timer1.Enabled = false;
                this.Hide();
                Form2 goster = new Form2(kadi );
                goster.ShowDialog();
                Application.Exit();
            }

        }

        private void progressBar1_Click(object sender, EventArgs e)
        {

        }
    }
}
